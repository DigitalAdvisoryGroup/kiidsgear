# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from datetime import datetime,date
import json
import random

class giftvoucher(WebsiteSale):

    @http.route(['/discount_cancel'], type='json', auth="public", website=True)
    def discount_cancel(self,discount,**post):
        if discount:
            sale_order_detail_id1=request.env['sale.order'].browse(request.session['sale_order_id'])
            if sale_order_detail_id1.sale_vouchercode:
                sale_order_detail_id1.sale_vouchercode =None
                sale_order_detail_id1.total_discount = 0.0
                sale_order_detail_id1.amount_total = sale_order_detail_id1.amount_untaxed
            return True

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        order_id = request.website.sale_get_order(force_create=1)
        if order_id.sale_vouchercode:
            order_id.sale_vouchercode = None
            order_id.total_discount = 0.0
            order_id.amount_total = order_id.amount_untaxed
        order_id._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values
        )
        return request.redirect("/shop/cart")

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        payment_confirm = super(giftvoucher, self).payment_confirmation(post=post)
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order_detail_voucher=request.env['sale.order'].sudo().browse(sale_order_id)
        voucher_detail=request.env['gift.voucher.detail'].sudo().search([('id','=',sale_order_detail_voucher.sale_vouchercode.id)])
        if sale_order_detail_voucher.sale_vouchercode:
            voucher_detail.write({'redeem_voucher_ids':[(0,0,{'customer_id':request.env.user.partner_id.id,'used_date':date.today(),'voucher_code':sale_order_detail_voucher.sale_vouchercode.code,'order_amount':sale_order_detail_voucher.amount_untaxed,'voucher_amount':sale_order_detail_voucher.total_discount,'order_name':sale_order_detail_voucher.name})]})
        return payment_confirm

    def discount_count(self,voucher,sale_order,tot,cnt_tot):
        if voucher.discount_type=='percentage':
            cnt_tot=(tot*voucher.discount)/100
            tot=tot-cnt_tot
        elif voucher.discount_type=='fixed':
            tot=tot-voucher.discount
            cnt_tot=voucher.discount
        sale_order.sudo().write({'total_discount':cnt_tot,'amount_total':tot,'sale_vouchercode':voucher.id})
        return True

    @http.route(['/discount_cart'], type='json', auth="public", website=True)
    def discount_cart(self,code,**post):
        current_date = date.today()
        if code:
            sum_qty,count_total,total=0,0,0
            voucher_detail_search=request.env['gift.voucher.detail'].sudo().search([('code','=',code)])
            voucher_detail=request.env['gift.voucher.detail'].sudo().search([('code','=',code),('expiry_date','>=',str(current_date))])
            if not voucher_detail_search:
                    return {'code':'Not valid voucher code'}
            sale_order_detail_id=request.env['sale.order'].sudo().browse(request.session['sale_order_id'])
            if voucher_detail and str(voucher_detail.expiry_date) >= str(current_date):
                sale_order_redeeption_count=request.env['sale.order'].sudo().search_count([('partner_id','=',request.env.user.partner_id.id),('sale_vouchercode','=',voucher_detail.id)])
                if sale_order_detail_id.amount_total < voucher_detail.discount:
                    return {'code':'Voucher discount greter then total amount'}
                if sale_order_detail_id.total_discount != 0:
                    return {'code':'You have already used voucher code'}
                if voucher_detail.redemption_customer > sale_order_redeeption_count:
                    for each1 in sale_order_detail_id.order_line:
                        sum_qty+=each1.product_uom_qty
                    total=sale_order_detail_id.amount_untaxed
                    if voucher_detail.voucher_type=='order_total':
                        if total>voucher_detail.minimum_amount:
                            return self.discount_count(voucher_detail,sale_order_detail_id,total,count_total)
                        else:
                            return {'code':'Order total amount is low to voucher limit'}
#                         elif voucher_detail.voucher_type=='quantity':
#                             if sum_qty>=voucher_detail.minimum_qty:
#                                 return self.discount_count(voucher_detail,sale_order_detail_id,total,count_total)
#                             else:
#                                 return {'code':'Order quantity is low'}
                    elif voucher_detail.voucher_type=='category':
                        category_list = []
                        child_cate = request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher_ee.child_cate')
                        if child_cate == False:
                            for order_cate in sale_order_detail_id.order_line:
                                category_list += order_cate.product_id.public_categ_ids.ids
                            if len(list(set(voucher_detail.category_type.ids) & set(category_list))) != 0:
                                return self.discount_count(voucher_detail,sale_order_detail_id,total,count_total)
                            else:
                                return {'code':'Category not match'}
                        else:
                            flag = True
                            for order_cate in sale_order_detail_id.order_line:
                                for each in order_cate.product_id.public_categ_ids:
                                    if each.id in voucher_detail.category_type.ids:
                                        return self.discount_count(voucher_detail,sale_order_detail_id,total,count_total)
                                    elif not each.parent_id:
                                        flag = False
                                    else:
                                        check_parent = self.checkParent(each, voucher_detail.category_type)
                                        if check_parent == True:
                                            return self.discount_count(voucher_detail,sale_order_detail_id,total,count_total)
                                        if check_parent == False:
                                            return {'code':'Category not match'}
                            if flag == False:
                                return {'code':'Category not match'}
                    return True
                else:
                    return {'code':'Voucher redeeption zero'}
            else:
                return {'code':'Expired your voucher'}
        else:
            return {'code':'Please enter voucher code'}

    def checkParent(self, cat_id, voucher_detail):
        if cat_id.parent_id.id in voucher_detail.ids:
            return True
        elif cat_id.parent_id.parent_id:
            self.checkParent(cat_id.parent_id, voucher_detail)
        else:
            return False

    @http.route(['/notification'], type='json', auth="public", website=True)
    def check_notification(self,**post):
        notifications = request.env['res.config.settings'].search([],limit=1,order='id desc')
        if notifications.voucher_show_option == 'notification':
            delaytime = notifications.delay_time
            if notifications.voucher_notification_show == 'pageload':
                return {'detail':'pageload',
                        'delaytime':delaytime}
            elif notifications.voucher_notification_show == 'intervaltime':
                minute = notifications.interval_time

                return {'detail':'intervaltime',
                                   'minute':minute,
                                    'delaytime':delaytime}


    @http.route(['/shownotification'], type='json', auth="public", website=True)
    def show_notification(self,**post):
        voucher_enable = request.env['ir.config_parameter'].sudo().get_param('aspl_website_gift_voucher_ee.gift_voucher')
        if voucher_enable == 'True':
            list=[]
            data = request.env['gift.voucher.detail'].search([]).read()
            while True:
                random_selected = random.SystemRandom().choice(data)
                if str(random_selected['expiry_date']) >= str(date.today()):
                    if random_selected['voucher_type'] == 'category':
                        for type in random_selected['category_type']:
                            categ_type = request.env['product.public.category'].browse(type)
                            for categ in categ_type:
                                list.append(categ.name)

                        if random_selected['discount_type'] == 'fixed':
                            message = "Flat <b>  "+str(random_selected['discount'])+"   Rs.</b> " +" off on  <br>"+"<b>"+ ', '.join(list)+" </b>  Products. <br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b><u>"+random_selected['code']
                            return {'message':message}

                        else:
                            message = "Flat <b>  "+str(random_selected['discount'])+"   % </b> " +" off on  <br>"+"<b>"+ ', '.join(list)+" </b>  Products. <br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b><u>"+random_selected['code']
                            return {'message': message}

                    else:

                        if random_selected['discount_type'] == 'fixed':
                            message = "Flat <b>  "+str(random_selected['discount'])+"   Rs. </b> " +" off on  <br> Total order Of "+"<b>"+str(random_selected['minimum_amount']) + " Rs.<br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b><u>"+random_selected['code']
                            return {'message': message}

                        else:
                            message = "Flat <b>  "+str(random_selected['discount'])+"   % </b> " +" off on  <br> Total order Of "+"<b>"+str(random_selected['minimum_amount']) + " Rs.<br> <br> <style='margin-left:40px;'> Use Code:-  "+"<b><u>"+random_selected['code']
                            return {'message': message}


    @http.route(['/voucher'], type='http', auth='public', website=True)
    def voucher_details_page(self, **kwargs):
        val = {
            'voucher_data': request.env['gift.voucher.detail'].search([])

        }
        return request.render("aspl_website_gift_voucher_ee.voucher_detail_template",val)



