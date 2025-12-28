class RiskManager:
    def position_size(self, cash, price, risk_pct=0.02):
        """
        Risk only 2% of cash per trade
        """
        capital = cash * risk_pct
        qty = int(capital // price)
        return max(qty, 0)