function SenceXBlock(runtime, element, settings) {

    $(function($) {
        /* Insert values into hidden form */
        const fill_hidden_form = (data) => {
            if(data['session_status'].is_active) {
                /* Logout */
                $(element).find('#form_sence').attr('action', data['logout_url']);
                $(element).find('#form_sence #UrlRetoma').val(data['UrlRetomaLogout']);
                $(element).find('#form_sence #UrlError').val(data['UrlErrorLogout']);
                $(element).find('#form_sence #IdSesionSence').val(data['session_status'].id_session);
            } else {
                /* Login */
                $(element).find('#form_sence').attr('action', data['login_url']);
                $(element).find('#form_sence #UrlRetoma').val(data['UrlRetomaLogin']);
                $(element).find('#form_sence #UrlError').val(data['UrlErrorLogin']);
            }
            $(element).find('#form_sence #RutOtec').val(data['RutOtec']);
            $(element).find('#form_sence #Token').val(data['Token']);
            $(element).find('#form_sence #CodSence').val(data['CodSence']);
            $(element).find('#form_sence #CodigoCurso').val(data['CodigoCurso']);
            $(element).find('#form_sence #LineaCapacitacion').val(data['LineaCapacitacion']);
            $(element).find('#form_sence #RunAlumno').val(data['RunAlumno']);
            $(element).find('#form_sence #IdSesionAlumno').val(data['IdSesionAlumno']);
            $(element).find('#form_sence #submit_form_sence').prop( "disabled", false );
        }

        /* Show student status (check if user has an active Sence session) */
        const show_student_status = (status) => {
            if( status.is_active ){
                $(element).find('.detail').html('<strong>Cuentas con una sesión activa en Sence.</strong>');
                $(element).find('#form_sence #submit_form_sence').val('Cerrar Sesión en Sence');
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
