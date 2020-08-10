# SENCE XBLOCK

![https://github.com/eol-uchile/sence-xblock/actions](https://github.com/eol-uchile/sence-xblock/workflows/Python%20application/badge.svg)

Show/hide unit components until students login to Sence

## **Platform** Configuration

To enable API have to setup your own variables.

    SENCE_RUT_OTEC = 'your_rut_otec'
    SENCE_TOKEN = 'your_sence_token'
    SENCE_API_URL = 'your_sence_api_url' # ends with '/'

The app will get this variables from *site configurations* (priority) or from *production.py* in the *lms and cms settings*.

## Session Expire Time

The default session expire time is 6 (hours). It can be modified by setting *SENCE_EXPIRE_TIME* at *production.py* in the *lms settings*. This value has to be a number of hours (integer).

## **Course** Configuration

To enable this app have to setup the course at */admin/sence/eolsencecoursesetup/*. **Course id**, **Sence Code**, **Sence Line** are Required.

## TESTS
**Prepare tests:**

    > cd .github/
    > docker-compose run --rm lms /openedx/requirements/sence-xblock/.github/test.sh

## TO DO:
- [ ] Attendance Report
