fallback.ready(function() {
    var feedback_form = $('#feedback_form')
    var feedback_form_token = $('#feedback_form').find('#id_token').val()
    var csrfmiddlewaretoken = $('#feedback_form').find('[name=csrfmiddlewaretoken]').val()
    feedback_form.find('[name=found_useful]').click(function(el) {
        var found_useful = $(this).val();
        $.post('/feedback/submit_initial/', {
            found_useful: found_useful,
            token: feedback_form_token,
            csrfmiddlewaretoken: csrfmiddlewaretoken,
            source_url: window.location.pathname
        });
    });
});
