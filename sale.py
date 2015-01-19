# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond import backend
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, Bool, If
from trytond.transaction import Transaction

__all__ = ['Sale', 'SaleLine']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    def _group_shipment_key(self, moves, move):
        # Group shipments by move planned_date, so one shipment is created
        # for each planned_date
        grouping = super(Sale, self)._group_shipment_key(moves, move)
        new_grouping = [('planned_date', move[1].planned_date)]
        for field, value in grouping:
            if field == 'planned_date':
                continue
            new_grouping.append((field, value))
        return tuple(new_grouping)


class SaleLine:
    __name__ = 'sale.line'
    manual_delivery_date = fields.Date('Manual Delivery Date', readonly=True)

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls.delivery_date.readonly = False
        cls.delivery_date.setter = 'set_delivery_date'

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor
        sql_table = cls.__table__()

        # Migration from 3.2
        table = TableHandler(cursor, cls, module_name)
        move_delivery_dates = (not table.column_exist('manual_delivery_date')
            and table.column_exist('delivery_date'))

        super(SaleLine, cls).__register__(module_name)

        if move_delivery_dates:
            cursor.execute(*sql_table.update(
                    columns=[sql_table.manual_delivery_date],
                    values=[sql_table.delivery_date]))
            table.drop_column('delivery_date')

    @fields.depends('product', 'quantity', '_parent_sale.sale_date',
        'manual_delivery_date')
    def on_change_with_delivery_date(self, name=None):
        if not self.product or not self.quantity:
            return
        if self.manual_delivery_date:
            return self.manual_delivery_date
        return super(SaleLine, self).on_change_with_delivery_date()

    @classmethod
    def set_delivery_date(cls, records, name, value):
        cls.write(records, {
                'manual_delivery_date': value,
                })
