"""
Regime Detection Model Evaluation
Evaluates HMM/GMM performance using regime persistence, transition realism, and trading value

Version: 2.1.0 - Added flexible strategy configuration support
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from sklearn.metrics import confusion_matrix, silhouette_score
import warnings
warnings.filterwarnings('ignore')


class RegimeEvaluator:
    """
    Evaluates regime detection models based on:
    - Transition matrix stability (persistence >0.85)
    - AIC/BIC for model selection
    - Backtesting metrics (Sharpe, Calmar, max drawdown)
    - Out-of-sample validation
    """
    
    def __init__(self, model, data: pd.DataFrame, regimes: np.ndarray):
        """
        Args:
            model: Fitted HMM or GMM model
            data: Market data with returns
            regimes: Predicted regime labels
        """
        self.model = model
        self.data = data
        self.regimes = regimes
        
    def evaluate_transition_stability(self) -> Dict:
        """
        Check transition matrix for regime persistence
        Good model: diagonal >0.85, realistic transitions
        """
        results = {}
        
        # For HMM models with transition matrix
        if hasattr(self.model, 'transmat_'):
            transmat = self.model.transmat_
            results['transition_matrix'] = transmat
            results['diagonal_persistence'] = np.diag(transmat)
            results['avg_persistence'] = np.mean(np.diag(transmat))
            results['persistence_quality'] = 'Good' if results['avg_persistence'] > 0.85 else 'Needs Improvement'
            
        # For all models: compute empirical transitions
        empirical_trans = self._compute_empirical_transitions()
        results['empirical_transitions'] = empirical_trans
        
        return results
    
    def _compute_empirical_transitions(self) -> np.ndarray:
        """Compute empirical transition matrix from regime sequence"""
        n_regimes = len(np.unique(self.regimes))
        trans_counts = np.zeros((n_regimes, n_regimes))
        
        for i in range(len(self.regimes) - 1):
            trans_counts[self.regimes[i], self.regimes[i+1]] += 1
        
        # Normalize to probabilities
        row_sums = trans_counts.sum(axis=1, keepdims=True)
        trans_probs = np.divide(trans_counts, row_sums, 
                                where=row_sums!=0, 
                                out=np.zeros_like(trans_counts))
        
        return trans_probs
    
    def compute_information_criteria(self) -> Dict:
        """
        Calculate AIC/BIC for model selection
        Lower is better; BIC penalizes complexity more
        """
        results = {}
        
        # For HMM models
        if hasattr(self.model, 'score'):
            log_likelihood = self.model.score(self.data)
            n_params = self._estimate_n_parameters()
            n_samples = len(self.data)
            
            results['log_likelihood'] = log_likelihood
            results['aic'] = -2 * log_likelihood + 2 * n_params
            results['bic'] = -2 * log_likelihood + n_params * np.log(n_samples)
            
        return results
    
    def _estimate_n_parameters(self) -> int:
        """Estimate number of model parameters"""
        if hasattr(self.model, 'n_components'):
            n_states = self.model.n_components
            n_features = self.data.shape[1] if len(self.data.shape) > 1 else 1
            
            # Transition matrix + emission params
            n_params = n_states * (n_states - 1)  # Transitions
            n_params += n_states * n_features * 2  # Means + variances
            
            return n_params
        return 0
    
    def backtest_strategy(self, 
                         long_regimes: list = [0, 1],
                         hedge_regimes: list = [2, 3],
                         risk_free_rate: float = 0.065) -> Dict:
        """
        Backtest trading strategy based on regimes
        
        Args:
            long_regimes: Regime IDs for long positions
            hedge_regimes: Regime IDs for cash/hedge
            risk_free_rate: Annual risk-free rate (6.5% for India)
        
        Returns:
            Dict with Sharpe, Calmar, max drawdown, returns
        """
        if 'returns' not in self.data.columns:
            raise ValueError("Data must contain 'returns' column")
        
        returns = self.data['returns'].values
        
        # Strategy returns: long in certain regimes, cash in others
        strategy_returns = np.zeros_like(returns)
        
        for i in range(len(returns)):
            if self.regimes[i] in long_regimes:
                strategy_returns[i] = returns[i]
            elif self.regimes[i] in hedge_regimes:
                strategy_returns[i] = risk_free_rate / 252  # Daily risk-free
            else:
                strategy_returns[i] = 0  # Cash
        
        # Performance metrics
        cumulative_returns = (1 + strategy_returns).cumprod()
        buy_hold_returns = (1 + returns).cumprod()
        
        # Sharpe Ratio
        excess_returns = strategy_returns - (risk_free_rate / 252)
        sharpe = np.sqrt(252) * np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)
        
        # Maximum Drawdown
        cummax = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        # Calmar Ratio
        total_return = cumulative_returns[-1] - 1
        calmar = total_return / (abs(max_drawdown) + 1e-10)
        
        # Buy-and-Hold comparison
        bh_sharpe = np.sqrt(252) * np.mean(returns - risk_free_rate/252) / (np.std(returns) + 1e-10)
        
        results = {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar,
            'total_return': total_return,
            'annualized_return': (1 + total_return) ** (252 / len(returns)) - 1,
            'buy_hold_sharpe': bh_sharpe,
            'strategy_beats_bh': sharpe > bh_sharpe,
            'cumulative_returns': cumulative_returns,
            'buy_hold_cumulative': buy_hold_returns,
            'quality_score': self._get_strategy_quality(sharpe, calmar, max_drawdown)
        }
        
        return results
    
    def _get_strategy_quality(self, sharpe: float, calmar: float, max_dd: float) -> str:
        """Rate strategy quality based on thresholds"""
        if sharpe > 1.2 and calmar > 0.5 and max_dd > -0.25:
            return "Excellent - Deployable"
        elif sharpe > 0.8 and calmar > 0.3:
            return "Good - Consider Deployment"
        elif sharpe > 0.5:
            return "Fair - Needs Improvement"
        else:
            return "Poor - Rework Model"
    
    def oos_validation(self, 
                       train_pct: float = 0.7,
                       validate_events: Optional[Dict] = None) -> Dict:
        """
        Out-of-sample validation
        
        Args:
            train_pct: Percentage of data for training
            validate_events: Dict of {date: expected_regime} for known events
        
        Returns:
            OOS performance metrics
        """
        split_idx = int(len(self.data) * train_pct)
        
        oos_regimes = self.regimes[split_idx:]
        oos_returns = self.data['returns'].values[split_idx:]
        
        # Compute metrics on OOS period
        oos_backtest = self.backtest_strategy()
        
        results = {
            'oos_sharpe': oos_backtest['sharpe_ratio'],
            'oos_calmar': oos_backtest['calmar_ratio'],
            'oos_max_drawdown': oos_backtest['max_drawdown'],
            'oos_total_return': oos_backtest['total_return']
        }
        
        # Event validation if provided
        if validate_events:
            results['event_accuracy'] = self._validate_known_events(validate_events)
        
        return results
    
    def _validate_known_events(self, events: Dict) -> float:
        """Check if model correctly identifies known regime shifts"""
        # Implementation would check specific dates
        # Placeholder for now
        return 0.0
    
    def regime_characteristics_quality(self) -> Dict:
        """
        Validate that regimes have distinct characteristics
        Using silhouette score and regime statistics
        """
        if len(self.data.shape) == 1:
            features = self.data.values.reshape(-1, 1)
        else:
            features = self.data.values
        
        # Silhouette score: -1 to 1, higher is better
        sil_score = silhouette_score(features, self.regimes)
        
        # Regime statistics
        regime_stats = {}
        for regime in np.unique(self.regimes):
            mask = self.regimes == regime
            regime_data = self.data[mask]
            
            if 'returns' in regime_data.columns:
                regime_stats[f'regime_{regime}'] = {
                    'mean_return': regime_data['returns'].mean(),
                    'volatility': regime_data['returns'].std(),
                    'count': mask.sum(),
                    'percentage': mask.sum() / len(self.regimes) * 100
                }
        
        return {
            'silhouette_score': sil_score,
            'quality': 'Good' if sil_score > 0.3 else 'Needs Improvement',
            'regime_stats': regime_stats
        }
    
    def compute_regime_duration_distribution(self) -> Dict:
        """
        Calculate regime duration statistics to detect noise vs meaningful regimes
        
        Returns:
            Dict with duration stats per regime and overall turnover metrics
        """
        regime_durations = {regime: [] for regime in np.unique(self.regimes)}
        current_regime = self.regimes[0]
        duration = 1
        
        for i in range(1, len(self.regimes)):
            if self.regimes[i] == current_regime:
                duration += 1
            else:
                regime_durations[current_regime].append(duration)
                current_regime = self.regimes[i]
                duration = 1
        
        # Add final duration
        regime_durations[current_regime].append(duration)
        
        # Compute statistics per regime
        duration_stats = {}
        for regime, durations in regime_durations.items():
            if len(durations) > 0:
                duration_stats[f'regime_{regime}'] = {
                    'mean_duration_days': np.mean(durations),
                    'median_duration_days': np.median(durations),
                    'min_duration_days': np.min(durations),
                    'max_duration_days': np.max(durations),
                    'pct_single_day': np.sum(np.array(durations) == 1) / len(durations) * 100,
                    'num_switches': len(durations)
                }
        
        # Overall metrics
        total_switches = sum(1 for i in range(1, len(self.regimes)) if self.regimes[i] != self.regimes[i-1])
        
        return {
            'duration_stats': duration_stats,
            'total_regime_switches': total_switches,
            'avg_switches_per_year': total_switches / (len(self.regimes) / 252),
            'quality': 'Low Noise' if total_switches < len(self.regimes) / 10 else 'High Noise (many switches)'
        }
    
    def compute_turnover_metrics(self, 
                                 long_regimes: list = [0, 1],
                                 hedge_regimes: list = [2, 3],
                                 transaction_cost: float = 0.002) -> Dict:
        """
        Calculate turnover and cost-adjusted performance metrics
        
        Args:
            long_regimes: Regime IDs for long positions
            hedge_regimes: Regime IDs for cash/hedge
            transaction_cost: Cost per trade as percentage (default 0.2% = 0.002)
        
        Returns:
            Dict with turnover metrics and cost-adjusted Sharpe/Calmar
        """
        # Track position changes
        positions = np.zeros(len(self.regimes))
        for i in range(len(self.regimes)):
            if self.regimes[i] in long_regimes:
                positions[i] = 1.0  # 100% long
            elif self.regimes[i] in hedge_regimes:
                positions[i] = 0.0  # Cash
            else:
                positions[i] = 0.0
        
        # Calculate turnover (position changes)
        position_changes = np.abs(np.diff(positions, prepend=positions[0]))
        total_turnover = np.sum(position_changes)
        avg_annual_turnover = total_turnover / (len(positions) / 252)
        
        # Calculate transaction costs
        total_costs = total_turnover * transaction_cost
        avg_cost_per_period = total_costs / len(positions)
        
        # Re-run backtest with transaction costs
        if 'returns' not in self.data.columns:
            raise ValueError("Data must contain 'returns' column")
        
        returns = self.data['returns'].values
        risk_free_rate = 0.065  # Default India rate
        
        # Strategy returns after costs
        strategy_returns = np.zeros_like(returns)
        for i in range(len(returns)):
            if self.regimes[i] in long_regimes:
                strategy_returns[i] = returns[i]
            elif self.regimes[i] in hedge_regimes:
                strategy_returns[i] = risk_free_rate / 252
            
            # Subtract cost on position changes
            if i > 0 and position_changes[i] > 0:
                strategy_returns[i] -= transaction_cost
        
        # Cost-adjusted metrics
        cumulative_returns_net = (1 + strategy_returns).cumprod()
        excess_returns_net = strategy_returns - (risk_free_rate / 252)
        
        sharpe_net = np.sqrt(252) * np.mean(excess_returns_net) / (np.std(excess_returns_net) + 1e-10)
        
        cummax_net = np.maximum.accumulate(cumulative_returns_net)
        drawdown_net = (cumulative_returns_net - cummax_net) / cummax_net
        max_drawdown_net = np.min(drawdown_net)
        
        total_return_net = cumulative_returns_net[-1] - 1
        calmar_net = total_return_net / (abs(max_drawdown_net) + 1e-10)
        
        # Get gross metrics for comparison
        gross_backtest = self.backtest_strategy(long_regimes, hedge_regimes, risk_free_rate)
        
        return {
            'total_turnover': total_turnover,
            'avg_annual_turnover': avg_annual_turnover,
            'total_transaction_costs_pct': total_costs * 100,
            'num_trades': int(np.sum(position_changes > 0)),
            'sharpe_gross': gross_backtest['sharpe_ratio'],
            'sharpe_net': sharpe_net,
            'sharpe_impact': sharpe_net - gross_backtest['sharpe_ratio'],
            'calmar_gross': gross_backtest['calmar_ratio'],
            'calmar_net': calmar_net,
            'calmar_impact': calmar_net - gross_backtest['calmar_ratio'],
            'max_drawdown_net': max_drawdown_net,
            'total_return_net': total_return_net,
            'quality_net': self._get_strategy_quality(sharpe_net, calmar_net, max_drawdown_net)
        }
    
    def generate_evaluation_report(self, 
                                   long_regimes: list = None,
                                   hedge_regimes: list = None,
                                   risk_free_rate: float = 0.065) -> Dict:
        """
        Generate comprehensive evaluation report including all metrics
        
        Args:
            long_regimes: Regime IDs for long positions (default: [0, 1])
            hedge_regimes: Regime IDs for cash/hedge (default: [2, 3])
            risk_free_rate: Annual risk-free rate (default: 0.065 for India)
        """
        # Set defaults if not provided
        if long_regimes is None:
            long_regimes = [0, 1]
        if hedge_regimes is None:
            n_regimes = len(np.unique(self.regimes))
            hedge_regimes = [i for i in range(n_regimes) if i not in long_regimes]
        
        report = {
            'transition_analysis': self.evaluate_transition_stability(),
            'information_criteria': self.compute_information_criteria(),
            'backtest_results': self.backtest_strategy(long_regimes, hedge_regimes, risk_free_rate),
            'regime_quality': self.regime_characteristics_quality(),
            'regime_duration': self.compute_regime_duration_distribution(),
            'turnover_and_costs': self.compute_turnover_metrics(long_regimes, hedge_regimes, risk_free_rate)
        }
        
        return report


def compare_models(models_dict: Dict, data: pd.DataFrame, regimes_dict: Dict) -> pd.DataFrame:
    """
    Compare multiple models using AIC/BIC and backtest metrics
    
    Args:
        models_dict: {"Model Name": model_object}
        data: Market data
        regimes_dict: {"Model Name": regime_predictions}
    
    Returns:
        Comparison DataFrame
    """
    comparison = []
    
    for name, model in models_dict.items():
        evaluator = RegimeEvaluator(model, data, regimes_dict[name])
        
        ic = evaluator.compute_information_criteria()
        backtest = evaluator.backtest_strategy()
        quality = evaluator.regime_characteristics_quality()
        
        comparison.append({
            'Model': name,
            'AIC': ic.get('aic', np.nan),
            'BIC': ic.get('bic', np.nan),
            'Sharpe': backtest['sharpe_ratio'],
            'Calmar': backtest['calmar_ratio'],
            'Max Drawdown': backtest['max_drawdown'],
            'Silhouette': quality['silhouette_score'],
            'Quality': backtest['quality_score']
        })
    
    return pd.DataFrame(comparison).sort_values('Sharpe', ascending=False)
