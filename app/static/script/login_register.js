function validatePasswords() {
    const password = document.getElementById('password_register').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return false;
    }
    return true;
}
