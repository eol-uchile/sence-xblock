function SenceXBlock(runtime, element, settings) {

    $(function($) {
        const show = ( {is_active, is_course_staff} ) => is_active || is_course_staff;
        console.log(show(settings));
        if(!show(settings)) {
            // hide all components except this xblock (sence message)
            $('.vert').not(`[data-id*="${settings.location}"]`).hide();
        }

    });
}
