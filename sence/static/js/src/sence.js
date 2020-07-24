function SenceXBlock(runtime, element, settings) {

    $(function($) {
        /* Insert values into hidden form */
        const fill_hidden_form = (data) => {
            $(element).find('#login_sence').attr('action', data['login_url']);
            $(element).find('#login_sence #RutOtec').val(data['RutOtec']);
            $(element).find('#login_sence #Token').val(data['Token']);
            $(element).find('#login_sence #CodSence').val(data['CodSence']);
            $(element).find('#login_sence #CodigoCurso').val(data['CodigoCurso']);
            $(element).find('#login_sence #LineaCapacitacion').val(data['LineaCapacitacion']);
            $(element).find('#login_sence #RunAlumno').val(data['RunAlumno']);
            $(element).find('#login_sence #IdSesionAlumno').val(data['IdSesionAlumno']);
            $(element).find('#login_sence #UrlRetoma').val(data['UrlRetoma']);
            $(element).find('#login_sence #UrlError').val(data['UrlError']);
            $(element).find('#login_sence #submit_login_sence').prop( "disabled", false );
        }

        /* Show student status (check if user has an active Sence session) */
        const show_student_status = (status) => {
            if( status.is_active ){
                $(element).find('.status').html('<p>Sesión Activa</p>');
                $(element).find('#login_sence #submit_login_sence').hide();
                $('.vert').not(`[data-id*="${settings.location}"]`).show();
            } else {
                $(element).find('.status').html('<p>Sesión Aún no iniciada</p>');
                /* If user is staff, show all components inside the unit */
                if(settings.is_course_staff) {
                    $('.vert').not(`[data-id*="${settings.location}"]`).show();
                }
            }
        }

        /* Load login data required from sence */
        const load_login_data = (url) => {

            // by default hide all components except this xblock (sence message)
            $('.vert').not(`[data-id*="${settings.location}"]`).hide();
            fetch(url)
                .then((response) => response.json())
                .then((response) => {
                    fill_hidden_form(response);
                    show_student_status(response['session_status']);
                })
                .catch((e) => console.log(e) );
        }

        load_login_data(settings.sence_login);

    });
}
