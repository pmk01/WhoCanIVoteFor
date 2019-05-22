(function () {
    "use strict";
    // This key is safe to be public
    var stripe = Stripe('pk_live_HzT3U8gpJzHFyBoR6A0BF5eu');
    var elements = stripe.elements();



    function AddStripeForm () {

        /**
         * Card Element
         */
        document.getElementById("payment-request-button").hidden = true;
        var card = elements.create("card", {
            iconStyle: "solid",
            style: {
                base: {
                    color: "#EC008C",
                    fontWeight: 500,
                    fontFamily: "sans-serif",
                    fontSize: "18px",
                    fontSmoothing: "antialiased",
                    lineHeight: "1.31",
                    padding: "8px",

                    "::placeholder": {
                        color: "#8b9299"
                    },
                    ":-webkit-autofill": {
                        color: "#EC008C"
                    }
                },
                invalid: {
                    color: "#b10e1e"
                }
            }
        });

        card.mount("#stripe_elements_container");
        document.getElementById("stripe_donate_form").hidden = false;

        var form = document.getElementById('stripe_donate_form');
        var DonateButton = document.createElement('button');
        DonateButton.setAttribute('type', 'submit');
        DonateButton.innerText = "Donate";
        form.appendChild(DonateButton);


        /* Errors */
        card.addEventListener('change', function (event) {
            var displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });

        // Create a token or display an error when the form is submitted.
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            stripe.createToken(card).then(function (result) {
                if (result.error) {
                    // Inform the customer that there was an error.
                    var errorElement = document.getElementById('card-errors');
                    errorElement.textContent = result.error.message;
                } else {
                    // Send the token to your server.
                    stripeTokenHandler(result.token);
                }
            });
        });

        function stripeTokenHandler(token) {
            // Insert the token ID into the form so it gets submitted to the server
            var form = document.getElementById('stripe_donate_form');
            var hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'stripeToken');
            hiddenInput.setAttribute('value', token.id);
            form.appendChild(hiddenInput);

            // Submit the form
            form.submit();
        }


    }



    function AddPaymentRequestAPI() {

        var paymentRequest = stripe.paymentRequest({
            country: 'GB',
            currency: 'gbp',
            total: {
                label: 'Democracy Club donation',
                amount: 500,
            },
            requestPayerName: true,
            requestPayerEmail: true,
            requestShipping: false,
        });

        var prButton = elements.create('paymentRequestButton', {
            paymentRequest: paymentRequest,
            style: {
                paymentRequestButton: {
                  type: 'donate',
                  theme: 'light-outline',
                  height: '64px', // default: '40px', the width is always '100%'
                },
              },
        });

        // Check the availability of the Payment Request API first.
        paymentRequest.canMakePayment().then(function (result) {
            if (result) {
                prButton.mount('#payment-request-button');
                document.getElementById("stripe_donate_form").hidden = true;
            } else {
                document.getElementById('payment-request-button').style.display = 'none';
                AddStripeForm();
            }
        });


        paymentRequest.on('token', function (ev) {
            // Send the token to your server to charge it!
            fetch('/donate/process_stripe', {
                method: 'POST',
                body: JSON.stringify({token: ev.token.id}),
                headers: {'content-type': 'application/json'},
            })
                .then(function (response) {
                    if (response.ok) {
                        // Report to the browser that the payment was successful, prompting
                        // it to close the browser payment interface.
                        ev.complete('success');
                    } else {
                        // Report to the browser that the payment failed, prompting it to
                        // re-show the payment interface, or show an error message and close
                        // the payment interface.
                        ev.complete('fail');
                    }
                });
        });

        paymentRequest.on('cancel', function (ev) {
           AddStripeForm();
        });
    }

    try {
        AddPaymentRequestAPI();

    } catch (e) {
        var form = document.getElementById('stripe_donate_form');
        form.innerHTML = document.getElementById('noscript_donate_button').innerHTML;
    }



})();
