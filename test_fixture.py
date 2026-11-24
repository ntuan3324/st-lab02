from ecommerce_app import fixture
# app, user, cart = fixture("600k")
# print("Subtotal:", cart.subtotal())
# print("Stock before:", {k:p.stock for k,p in app.catalog.products.items()})
# order = app.place(user, cart, voucher="SAVE10", method="COD", key="DEMO-001")
# print("Order ID:", order.order_id)
# print("Discount:", order.discount, "Shipping:", order.shipping, "Total:", order.total)
# print("Stock after:", {k:p.stock for k,p in app.catalog.products.items()})

app, user, cart = fixture("600k")
print("Subtotal:", cart.subtotal())
print("Stock before:", {k: p.stock for k, p in app.catalog.products.items()})
