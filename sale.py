#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, Bool, If

__all__ = ['SaleLine']
__metaclass__ = PoolMeta


class SaleLine:
    __name__ = 'sale.line'
    delivery_date = fields.Date('Delivery Date',
            states={
                'invisible': ((Eval('type') != 'line')
                    | (If(Bool(Eval('quantity')), Eval('quantity', 0), 0)
                        <= 0)),
                },
            depends=['type', 'quantity'])

    @fields.depends('product', 'quantity', '_parent_sale.sale_date',
        'delivery_date')
    def on_change_with_delivery_date(self):
        if not self.product or not self.quantity:
            return
        date = super(SaleLine, self).on_change_with_delivery_date()
        if not self.delivery_date:
            return date
        return self.delivery_date
