


b={
    "money":100,
    "pay_type":"1",
    "trade_type":"T1"
}
a='/{"money":{money},"pay_type":"{pay_type}","trade_type":"{trade_type}"/}'

print(a.format(**b))