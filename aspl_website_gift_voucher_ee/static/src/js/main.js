odoo.define('aspl_website_gift_voucher.main',function(require){
	"use strict";

	$(document).ready(function(){
		var ajax = require('web.ajax');

		$('#mycar').carousel();
		$("#btn_cancel_voucher_code").click(function(){
			var discount =$('.discount_count').text();
			ajax.jsonRpc('/discount_cancel', 'call', {
				'discount':discount,
			})
			.then(function(result){
				if (result){
					location.reload(true);
					$('#order_total_taxes1').hide();
				}
			});
		});

		$(".btn-clicked").keyup(function(event){
		    if(event.keyCode == 13){
		        $("#btn_apply_voucher_code").click();
		    }
		});

		$("#btn_apply_voucher_code").click(function(){
			
			var code = $("#code_no").val();
			ajax.jsonRpc('/discount_cart', 'call', {
				'code':code,
			})
			.then(function(result){
				if (result==true){
					location.reload(true);
				}
				if (result.code){
					swal(result.code,"","error")
				}
				$('#code_no').val('');
			});
		});
	});
});

//this file save with "main.js"
