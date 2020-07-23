function SenceXBlock(runtime, element, settings) {

    $(function($) {
        /* Only for testing */
        const show = ( {is_active, is_course_staff} ) => is_active || is_course_staff;

        /* Load login data required from sence */
        const load_login_data = (url) => {
            fetch(url)
                .then((response) => response.json())
                .then((response) => {
                    /* insert values into form */
                    $(element).find('#login_sence').attr('action', response['login_url']);
                    $(element).find('#login_sence #RutOtec').val(response['RutOtec']);
                    $(element).find('#login_sence #Token').val(response['Token']);
                    $(element).find('#login_sence #CodSence').val(response['CodSence']);
                    $(element).find('#login_sence #CodigoCurso').val(response['CodigoCurso']);
                    $(element).find('#login_sence #LineaCapacitacion').val(response['LineaCapacitacion']);
                    $(element).find('#login_sence #RunAlumno').val(response['RunAlumno']);
                    $(element).find('#login_sence #IdSesionAlumno').val(response['IdSesionAlumno']);
                    $(element).find('#login_sence #UrlRetoma').val(response['UrlRetoma']);
                    $(element).find('#login_sence #UrlError').val(response['UrlError']);
                    $(element).find('#login_sence #submit_login_sence').prop( "disabled", false );
                })
                .catch((e) => console.log(e) );
        }

        load_login_data(settings.sence_login);

        if(!show(settings)) {
            // hide all components except this xblock (sence message)
            $('.vert').not(`[data-id*="${settings.location}"]`).hide();
        }

    });
}
