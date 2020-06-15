
function Click_Sign_in_with_google() {
    location.href="{% url 'social:begin' 'google-oauth2' %}?next={{ lab_hash }};"
}
function Click_to_Sign_Up_form() {
    location.href="{% url 'kmutnbtrackapp:signup' %}?next={{ lab_hash }};"
}