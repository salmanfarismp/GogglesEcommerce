

$ (document).ready(function(){

    var id =  $('#order_id').html();
    $('.payWithRazorpay').click(function(e){

        e.preventDefault();

        $.ajax({
            method: 'GET',
            url: "/pay_razorpay",
            success: function(response){
                console.log(response)
                var options = {
                    "key": "rzp_test_bjt6RpBlusedwC", // Enter the Key ID generated from the Dashboard
                    "amount": response.total_price * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                    "currency": "INR",
                    "name": "GOGGLES Corporate",
                    "description": "Secured",
                    "image": "https://example.com/your_logo",
                    // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                    "handler": function (responseb){
                        
                        data = {
                                'order_id': responseb.razorpay_payment_id,
                        }
                        $.ajax({
                            
                            method :"POST",
                            url: "/order_by_razorpay",
                            data: data,
                            success: function (responsec) {
                                Swal.fire(
                                  'Payment Success',
                                  'Order Placed!',
                                  'success'
                                ).then((result) => {
                                    window.location.href = '/invoice/' + id
                                  })
                                
                                
                            }
                        });
                
                    },
                    "prefill": {
                        "name": response.full_name,
                        "email": response.email,
                        "contact": response.phone_number,
                    },
                    "notes": {
                        "address": "Razorpay Corporate Office"
                    },
                    "theme": {
                        "color": "#3399cc"
                    }
                };
                var rzp1 = new Razorpay(options);
                rzp1.open();

            }
        })

       
    });
});


