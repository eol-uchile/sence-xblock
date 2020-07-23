# SENCE XBLOCK

Show/hide unit components until students login to Sence

## **Platform** Configuration

To enable API have to setup your own variables.

    SENCE_RUT_OTEC = 'your_rut_otec'
    SENCE_TOKEN = 'your_sence_token'
    SENCE_API_URL = 'your_sence_api_url'

The app will get this variables from *site configurations* (priority) or from *production.py* in the *lms settings*.

## **Course** Configuration

To enable this app have to setup the course at */admin/sence/eolsencecoursesetup/*. **Course id**, **Sence Code**, **Sense Line** are Required.

