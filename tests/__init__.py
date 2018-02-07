# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.sale_delivery_date.tests.test_sale_delivery_date import suite
except ImportError:
    from .test_sale_delivery_date import suite

__all__ = ['suite']
