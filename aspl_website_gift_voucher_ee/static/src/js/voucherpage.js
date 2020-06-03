odoo.define('aspl_website_gift_voucher.voucherpage',function(require){
	"use strict";

    var ajax=require('web.ajax');
    $(document).ready(function(){
        $('.see-the-offer-active').hide();

        $(".see-the-offer").click(function() {
                $(this).hide();
                $(this).parent().find('.see-the-offer-active').show();
                if ($(this).parent().find('.see-the-offer-active')){
                    $('.copy-btn').click(function(){
                        var code = $(this).parent().find('.code-detail').text().trim();
                        var $temp = $("<input>");
                        $("body").append($temp);
                        $temp.val(code).select();
                        document.execCommand("copy");
                        $temp.remove();
                        $(this).text('COPIED');
                    });
                }
        });
    });
});

