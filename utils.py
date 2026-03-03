import math

def emi(principal: float, annual_rate_percent: float, months: int) -> float:
    if months <= 0:
        raise ValueError('Months must be > 0')
    r = annual_rate_percent / 100.0 / 12.0
    if r == 0:
        return principal / months
    emi_val = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return emi_val

def sip_future_value(monthly_investment: float, annual_return_percent: float, years: float) -> float:
    r = annual_return_percent / 100.0 / 12.0
    n = int(years * 12)
    if r == 0:
        return monthly_investment * n
    fv = monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)
    return fv

def savings_goal_needed(target_amount: float, current_savings: float, annual_return_percent: float, years: float) -> float:
    r = annual_return_percent / 100.0 / 12.0
    n = int(years * 12)
    pv = current_savings
    if r == 0:
        return max(0.0, (target_amount - pv) / n)
    factor = (((1 + r) ** n - 1) / r) * (1 + r)
    needed = max(0.0, (target_amount - pv) / factor)
    return needed

def simple_tax_estimator(annual_income: float) -> dict:
    income = annual_income
    tax = 0.0
    brackets = [(250000, 0.0), (500000, 0.05), (1000000, 0.2), (float('inf'), 0.3)]
    remaining = income
    lower = 0.0
    for upper, rate in brackets:
        taxable = max(0.0, min(remaining, upper - lower))
        tax += taxable * rate
        remaining -= taxable
        lower = upper
        if remaining <= 0:
            break
    return {'estimated_tax': round(tax,2), 'effective_rate': round((tax/income*100) if income>0 else 0.0,2)}
