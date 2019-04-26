if ($('#feedback_form input[name=found_useful]:checked').val() == undefined) {
    $("#feedback_form .comments_container").hide()
    $('#feedback_form input[name=found_useful]').click(function() {
        $("#feedback_form .comments_container").show()
    })
}

$("#donate_button").on("click", function(el) {
   if (typeof(ga) === "undefined") {
        return true;
   } else {
       el.preventDefault();
       var url = el.target.href, split_test = $(el.target).data('split_test');
       try {
           ga('send', 'event', 'donate_link', 'click', split_test, {
               'transport': 'beacon',
               'hitCallback': function(){
                   document.location = url;
               }

           });
       } catch (e) {
           document.location = url;
       }
   }
});
