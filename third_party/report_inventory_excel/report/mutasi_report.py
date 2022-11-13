# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class MutasiReport(models.Model):
    _name = "mutasi.report"
    _description = "Mutasi Report"
    _auto = False
    _rec_name = 'prod_name'
    _order = 'prod_name asc'

    id = fields.Integer(string="ID")
    prod_id = fields.Many2one('product.product', 'Product Details')
    categ_id = fields.Many2one('product.category', 'Category')
    prod_code = fields.Char(string="Product Code")
    prod_name = fields.Char(string="Product Name")
    uom = fields.Char(String="Unit of Measure")
    saldo_awal = fields.Float('Saldo Awal')
    masuk = fields.Float('Barang Masuk')
    keluar = fields.Float('Barang Keluar')
    adjusment = fields.Float('Adjustment')
    stock_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Char('Selisih')
    keterangan = fields.Float('Keterangan')
    
    def _query(self):
        query = """
            select pp.id as id, 
                pp.id as prod_id,
                pt.categ_id as categ_id,
				pt.default_code as prod_code, 
				pt.name as prod_name,
				pu.name as uom,
				sum(coalesce(awal.qty,0)) as saldo_awal, 
                sum(coalesce(saldo_masuk.qty,0)) as masuk, 
                sum(coalesce(saldo_keluar.qty,0)) as keluar,
                sum(coalesce(prod_adj.qty,0)) as adjusment,
                (sum(coalesce(awal.qty,0)) + sum(coalesce(saldo_masuk.qty,0)) - sum(coalesce(saldo_keluar.qty,0)) + sum(coalesce(prod_adj.qty,0))) as saldo_akhir,
                (sum(coalesce(awal.qty,0)) + sum(coalesce(saldo_masuk.qty,0)) - sum(coalesce(saldo_keluar.qty,0)) + sum(coalesce(prod_adj.qty,0))) as saldo_opname,
                0 as selisih,
                'sesuai' as keterangan
                    
                from product_product pp
                    left join
                        (
                            select sm.product_id, sm.product_uom as uom, 
                            sum(case when sl.usage = 'internal' and dl.usage != 'internal'
                                then sm.product_uom_qty*-1 
                            when sl.usage != 'internal' and dl.usage = 'internal' 
                                then sm.product_uom_qty else 0 end) as qty
                            
                            from stock_move sm 
                            left join stock_location sl on sl.id = sm.location_id
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where sm.state = 'done' and sm.inventory_id is null
                            group by sm.product_id, sm.product_uom
                        ) awal on awal.product_id=pp.id
                        
                    left join 
                        (
                            select sm.product_id, sm.product_uom as uom, 
                            sum(sm.product_uom_qty) as qty 
                            from stock_move sm 
                            left join stock_location sl on sl.id = sm.location_id 
                            left join stock_location dl on dl.id = sm.location_dest_id 
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where sl.usage != 'internal' and dl.usage = 'internal' and sm.state = 'done' and sm.inventory_id is null 
                            group by sm.product_id, sm.product_uom
                        ) saldo_masuk on saldo_masuk.product_id=pp.id
                        
                    left join 
                        (
                            select sm.product_id, sm.product_uom as uom, sum(sm.product_uom_qty) as qty 
                            from stock_move sm 
                            left join stock_location sl on sl.id = sm.location_id 
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id	
                            left join uom_uom pu on pu.id= sm.product_uom 
                            where sl.usage = 'internal' and dl.usage != 'internal' and sm.state = 'done' and sm.inventory_id is null
                            group by sm.product_id, sm.product_uom
                        ) saldo_keluar on saldo_keluar.product_id=pp.id
                
                    left join
                        (
                            select sm.product_id, sm.product_uom as uom, 
                            sum(case when sl.usage = 'internal' and dl.usage != 'internal' and inventory_id is not null
                                then sm.product_uom_qty*-1 
                            when sl.usage != 'internal' and dl.usage = 'internal' and inventory_id is not null
                                then sm.product_uom_qty else 0 end ) as qty
                            
                            from stock_move sm 
                            left join stock_location sl on sl.id = sm.location_id
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where sm.state = 'done'
                            group by sm.product_id, sm.product_uom
                        ) prod_adj on prod_adj.product_id=pp.id
                
                
                left join product_template pt on pt.id=pp.product_tmpl_id
                left join uom_uom pu on pt.uom_id=pu.id
                    and (coalesce(awal.qty,0) != 0 
                    or coalesce(saldo_masuk.qty,0) != 0 
                    or coalesce(saldo_keluar.qty,0) != 0) 
                    
                group by pt.default_code, pt.name, pp.id , pu.name, pt.categ_id 
                    order by pt.name asc
        """
        return query

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
