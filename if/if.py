freeShippingAllowed = False
shippingCost = 20.00
basketValue = 74.99
shippingModifier = 0.00
taxRate = 0.08

if basketValue >= 75 :
	freeShippingAllowed = True
	expressShipping = 5.00
	shippingCost = 0.00
	print("Free standard shipping allowed!")
else :
	freeShippingAllowed = False
	expressShipping = 10.00
	
expressShippingWanted = input("Do you want express shipping for an extra ${0:.2f}? ".format(expressShipping))
if expressShippingWanted.lower() == "y" or expressShippingWanted.lower() == "yes" :
	shippingModifier = expressShipping
	
shippingCostTotal = shippingCost + shippingModifier
taxTotal = (basketValue + shippingCostTotal) * taxRate
print(" Basket value: ${0:6.2f}".format(basketValue))
print("Shipping cost: ${0:6.2f}".format(shippingCostTotal))
print("   Tax @ {0:3.2f}: ${1:6.2f}".format(taxRate, taxTotal))
print("        Total: ${0:6.2f}".format(float(basketValue + shippingCostTotal + taxTotal)))
