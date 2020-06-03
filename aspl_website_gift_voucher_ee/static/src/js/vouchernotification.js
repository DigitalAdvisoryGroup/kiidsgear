odoo.define('aspl_website_gift_voucher.vouchernotification',function(require){
	"use strict";

    var ajax=require('web.ajax');
    $(document).ready(function (){
        ajax.jsonRpc('/notification', 'call',{})
        .then(function(data){
        if(data){
            var delaytime = data['delaytime']*1000
            if(data){
                if (data.detail == "pageload"){
                    datacall(delaytime)
                }

                else if (data['detail'] == "intervaltime"){
                  var minute = data['minute']
                  var minuteconvert = minute*60000
                    setInterval(function() {
                        datacall(delaytime)
                    }, minuteconvert);

                }
            }
            }
        });
    });

    function datacall(delaytime){
        ajax.jsonRpc('/shownotification', 'call',{})
            .then(function(data){
             if (data){
                     $.notify({
                                    message: data.message
                                },{

                                    type: 'pastel-info',
                                    delay: delaytime,
                                    template: '<div data-notify="container" class="col-xs-11 col-sm-3 alert alert-{0}" role="alert">' +
                                       '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">&times;</button>'+
                                       '<span data-notify="message">{2}</span>' +
                                       '</div>'
                     });
                }
            });
    }
});






