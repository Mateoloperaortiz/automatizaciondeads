// Validación del lado del cliente para los formularios de configuración
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a los formularios
    const metaForm = document.getElementById('meta-form');
    const geminiForm = document.getElementById('gemini-form');
    const googleForm = document.getElementById('google-form');

    // Referencias a los botones
    const metaTestBtn = document.querySelector('button[value="test_meta"]');
    const geminiTestBtn = document.querySelector('button[value="test_gemini"]');
    const googleTestBtn = document.querySelector('button[value="test_google"]');

    // Referencias a los campos de formulario Meta
    const metaAppId = document.getElementById('app_id');
    const metaAppSecret = document.getElementById('app_secret');
    const metaAccessToken = document.getElementById('access_token');
    const metaAdAccountId = document.getElementById('ad_account_id');
    const metaPageId = document.getElementById('page_id');

    // Referencias a los campos de formulario Gemini
    const geminiApiKey = document.getElementById('api_key');
    const geminiModel = document.getElementById('gemini_model');

    // Referencias a los indicadores de carga
    const metaLoader = document.getElementById('meta-loader');
    const geminiLoader = document.getElementById('gemini-loader');
    const googleLoader = document.getElementById('google-loader');

    // Tooltips para modelos Gemini
    initializeGeminiTooltips();

    // Validación para el formulario de Meta API
    if (metaForm) {
        metaForm.addEventListener('submit', function(e) {
            const action = document.activeElement.value;
            if (action === 'test_meta') {
                // Establecer el campo oculto para indicar que es una prueba de conexión
                document.getElementById('meta_test_connection').value = '1';

                // Validar el formulario
                if (!validateMetaForm()) {
                    e.preventDefault();
                } else {
                    showLoader(metaLoader, metaTestBtn);
                }
            }
        });

        // Validación en tiempo real para campos de Meta
        [metaAppId, metaAppSecret, metaAccessToken, metaAdAccountId, metaPageId].forEach(field => {
            if (field) {
                field.addEventListener('input', function() {
                    validateField(field);
                });
                field.addEventListener('blur', function() {
                    validateField(field);
                });
            }
        });
    }

    // Validación para el formulario de Gemini API
    if (geminiForm) {
        geminiForm.addEventListener('submit', function(e) {
            const action = document.activeElement.value;
            if (action === 'test_gemini') {
                // Establecer el campo oculto para indicar que es una prueba de conexión
                document.getElementById('gemini_test_connection').value = '1';

                // Validar el formulario
                if (!validateGeminiForm()) {
                    e.preventDefault();
                } else {
                    showLoader(geminiLoader, geminiTestBtn);
                }
            }
        });

        // Validación en tiempo real para campos de Gemini
        if (geminiApiKey) {
            geminiApiKey.addEventListener('input', function() {
                validateField(geminiApiKey);
            });
            geminiApiKey.addEventListener('blur', function() {
                validateField(geminiApiKey);
            });
        }
    }

    // Validación para el formulario de Google Ads API
    if (googleForm) {
        googleForm.addEventListener('submit', function(e) {
            const action = document.activeElement.value;
            if (action === 'test_google' && !validateGoogleForm()) {
                e.preventDefault();
            } else if (action === 'test_google') {
                showLoader(googleLoader, googleTestBtn);
            }
        });
    }

    // Función para validar el formulario de Meta API
    function validateMetaForm() {
        let isValid = true;

        if (metaAppId) {
            isValid = validateField(metaAppId) && isValid;
        }
        if (metaAppSecret) {
            isValid = validateField(metaAppSecret) && isValid;
        }
        if (metaAccessToken) {
            isValid = validateField(metaAccessToken) && isValid;
        }
        if (metaAdAccountId) {
            isValid = validateField(metaAdAccountId) && isValid;
        }
        if (metaPageId) {
            isValid = validateField(metaPageId) && isValid;
        }

        return isValid;
    }

    // Función para validar el formulario de Gemini API
    function validateGeminiForm() {
        let isValid = true;

        if (geminiApiKey) {
            isValid = validateField(geminiApiKey) && isValid;
        }

        return isValid;
    }

    // Función para validar el formulario de Google Ads API
    function validateGoogleForm() {
        // Implementar validación específica para Google Ads
        return true;
    }

    // Función para validar un campo individual
    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Eliminar mensaje de error existente
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Validación específica según el campo
        if (field.id === 'app_id') {
            if (!value) {
                isValid = false;
                errorMessage = 'El App ID es requerido';
            } else if (!/^\d+$/.test(value)) {
                isValid = false;
                errorMessage = 'El App ID debe contener solo números';
            }
        } else if (field.id === 'app_secret') {
            if (!value) {
                isValid = false;
                errorMessage = 'El App Secret es requerido';
            } else if (value.length < 10) {
                isValid = false;
                errorMessage = 'El App Secret debe tener al menos 10 caracteres';
            }
        } else if (field.id === 'access_token') {
            if (!value) {
                isValid = false;
                errorMessage = 'El Access Token es requerido';
            } else if (value.length < 20) {
                isValid = false;
                errorMessage = 'El Access Token debe tener al menos 20 caracteres';
            }
        } else if (field.id === 'ad_account_id') {
            if (!value) {
                isValid = false;
                errorMessage = 'El Ad Account ID es requerido';
            } else if (!/^act_\d+$/.test(value)) {
                isValid = false;
                errorMessage = 'El Ad Account ID debe tener el formato act_XXXXXXXXXX';
            }
        } else if (field.id === 'page_id') {
            if (!value) {
                isValid = false;
                errorMessage = 'El Page ID es requerido';
            } else if (!/^\d+$/.test(value)) {
                isValid = false;
                errorMessage = 'El Page ID debe contener solo números';
            }
        } else if (field.id === 'api_key') {
            if (!value) {
                isValid = false;
                errorMessage = 'La API Key es requerida';
            } else if (value.length < 5) {
                isValid = false;
                errorMessage = 'La API Key debe tener al menos 5 caracteres';
            }
        }

        // Mostrar mensaje de error si es necesario
        if (!isValid) {
            field.classList.add('border-red-500');
            const errorElement = document.createElement('p');
            errorElement.className = 'error-message text-sm text-red-600 mt-1';
            errorElement.textContent = errorMessage;
            field.parentNode.appendChild(errorElement);
        } else {
            field.classList.remove('border-red-500');
        }

        return isValid;
    }

    // Función para mostrar el indicador de carga
    function showLoader(loader, button) {
        if (loader && button) {
            loader.classList.remove('hidden');
            button.disabled = true;

            // Restaurar el botón después de 10 segundos (por si hay un error)
            setTimeout(function() {
                loader.classList.add('hidden');
                button.disabled = false;
            }, 10000);
        }
    }

    // Función para inicializar tooltips para modelos Gemini
    function initializeGeminiTooltips() {
        const modelSelect = document.getElementById('gemini_model');
        if (modelSelect) {
            const options = modelSelect.querySelectorAll('option');
            options.forEach(option => {
                if (option.title) {
                    const tooltipId = 'tooltip-' + option.value.replace(/\//g, '-');

                    // Crear tooltip si no existe
                    if (!document.getElementById(tooltipId)) {
                        const tooltip = document.createElement('div');
                        tooltip.id = tooltipId;
                        tooltip.className = 'hidden absolute z-10 bg-gray-800 text-white p-2 rounded text-sm max-w-xs';
                        tooltip.textContent = option.title;
                        document.body.appendChild(tooltip);
                    }
                }
            });

            // Mostrar tooltip al pasar el mouse sobre la opción seleccionada
            modelSelect.addEventListener('mouseover', function() {
                const selectedOption = modelSelect.options[modelSelect.selectedIndex];
                if (selectedOption.title) {
                    const tooltipId = 'tooltip-' + selectedOption.value.replace(/\//g, '-');
                    const tooltip = document.getElementById(tooltipId);
                    if (tooltip) {
                        const rect = modelSelect.getBoundingClientRect();
                        tooltip.style.left = rect.left + 'px';
                        tooltip.style.top = (rect.bottom + 5) + 'px';
                        tooltip.classList.remove('hidden');
                    }
                }
            });

            modelSelect.addEventListener('mouseout', function() {
                const tooltips = document.querySelectorAll('[id^="tooltip-"]');
                tooltips.forEach(tooltip => {
                    tooltip.classList.add('hidden');
                });
            });
        }
    }
});
