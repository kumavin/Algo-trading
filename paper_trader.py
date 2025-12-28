# # class PaperTrader:
# #     def __init__(self, cash=1_000_000):
# #         self.cash = cash
# #         self.positions = {}   # stock -> {qty, entry}

# #     def buy(self, stock, price, qty):
# #         """
# #         Execute a paper BUY
# #         """
# #         cost = price * qty

# #         if qty <= 0:
# #             return False

# #         if cost > self.cash:
# #             return False

# #         self.cash -= cost
# #         self.positions[stock] = {
# #             "qty": qty,
# #             "entry": price
# #         }
# #         return True

# #     def sell(self, stock, price):
# #         """
# #         Execute a paper SELL (full exit)
# #         """
# #         if stock not in self.positions:
# #             return False

# #         qty = self.positions[stock]["qty"]
# #         self.cash += qty * price
# #         del self.positions[stock]
# #         return True

# #     def value(self, live_prices):
# #         """
# #         Portfolio value = cash + MTM positions
# #         """
# #         val = self.cash
# #         for s, pos in self.positions.items():
# #             if s in live_prices:
# #                 val += pos["qty"] * live_prices[s]
# #         return val

# class PaperTrader:
#     def __init__(self, cash=1_000_000):
#         self.cash = cash
#         self.positions = {}   # stock -> {qty, entry, high}

#     def buy(self, stock, price, qty):
#         if qty <= 0:
#             return False

#         cost = price * qty
#         if cost > self.cash:
#             return False

#         self.cash -= cost
#         self.positions[stock] = {
#             "qty": qty,
#             "entry": price,
#             "high": price    # 🔥 track highest price
#         }
#         return True

#     def sell(self, stock, price):
#         if stock not in self.positions:
#             return False

#         qty = self.positions[stock]["qty"]
#         self.cash += qty * price
#         del self.positions[stock]
#         return True

#     def value(self, live_prices):
#         val = self.cash
#         for s, pos in self.positions.items():
#             if s in live_prices:
#                 val += pos["qty"] * live_prices[s]
#         return val

from datetime import datetime


class PaperTrader:
    def __init__(self, cash=1_000_000):
        self.cash = cash

        # stock -> {qty, entry, high, entry_time}
        self.positions = {}

    def buy(self, stock, price, qty):

        if qty <= 0:
            return False

        cost = price * qty
        if cost > self.cash:
            return False

        self.cash -= cost

        self.positions[stock] = {
            "qty": qty,
            "entry": price,
            "high": price,

            # timestamp used for holding duration
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return True

    def sell(self, stock, price):

        if stock not in self.positions:
            return False

        qty = self.positions[stock]["qty"]
        self.cash += qty * price

        del self.positions[stock]
        return True

    def value(self, live_prices):

        val = self.cash

        for s, pos in self.positions.items():
            if s in live_prices and live_prices[s]:
                val += pos["qty"] * live_prices[s]

        return val

    # -------------------------------
    # ⭐ Auto-migrate legacy positions
    # -------------------------------
    def ensure_entry_time(self):
        """
        Some old trades stored before update lack entry_time.
        Assigns current time as fallback so holding days is never None.
        """

        changed = False

        for s, pos in self.positions.items():

            if "entry_time" not in pos or not pos["entry_time"]:
                pos["entry_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                changed = True

        return changed