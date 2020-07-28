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
                $(element).find('.detail').html('<strong>Cuentas con una sesión activa en Sence.</strong>');
                $(element).find('#login_sence #submit_login_sence').hide();
                $(element).find('.help').hide();
                $('.vert').not(`[data-id*="${settings.location}"]`).show();
            } else {
                /* If user is staff, show all components inside the unit */
                if(settings.is_course_staff) {
                    $('.vert').not(`[data-id*="${settings.location}"]`).show();
                    $(element).find('.detail').append('</br><strong style="color: red;">Los componentes son visibles porque estas viendo esta unidad como Equipo</strong>');
                }
            }
        }

        /* Load login data required from sence */
        const load_login_data = (url) => {
            $(element).find('.sence-content').hide();
            $(element).find('.loading').show();
            // by default hide all components except this xblock
            $('.vert').not(`[data-id*="${settings.location}"]`).hide();
            fetch(url)
                .then((response) => response.json())
                .then((response) => {
                    /* Show error message if exists */
                    if(response['error']) {
                        console.error(response);
                        if(response['error'] == 'sence_course_code') {
                            $(element).find('.loading').html('No se le ha asignado código de curso. Contacte al equipo docente para solucionar el problema.');
                        } else {
                            $(element).find('.loading').html('Hubo un problema al obtener los datos Sence. Recarge la página para intentar nuevamente.');
                        }
                        return;
                    }
                    $(element).find('.sence-content').show();
                    $(element).find('.loading').hide();
                    fill_hidden_form(response);
                    show_student_status(response['session_status']);
                })
                .catch((e) => {
                    console.error(e);
                    $(element).find('.loading').html('Hubo un problema al obtener los datos Sence. Recarge la página para intentar nuevamente.');
                } );
        }

        load_login_data(settings.sence_login);

    });
}
