document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calcForm');
    const calculateBtn = document.getElementById('calculateBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const resetBtn = document.getElementById('resetBtn');
    const errorBlock = document.getElementById('errorBlock');
    const resultBlock = document.getElementById('resultBlock');
    const cycleLengthSelect = document.getElementById('cycle_length');
    const lastPeriodInput = document.getElementById('last_period');

    // Populate cycle length options
    for (let i = 20; i <= 40; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === 28) option.selected = true;
        cycleLengthSelect.appendChild(option);
    }

    // Set max date for last period to today
    const today = new Date().toISOString().split('T')[0];
    lastPeriodInput.max = today;

    // Form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        calculatePregnancy();
    });

    // Reset button handler
    resetBtn.addEventListener('click', function() {
        form.reset();
        cycleLengthSelect.value = '28';
        hideResults();
        hideError();
        resetBtn.style.display = 'none';
    });

    // Real-time calculation on input change
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            if (lastPeriodInput.value) {
                calculatePregnancy();
            }
        });
    });

    function calculatePregnancy() {
        const formData = new FormData(form);
        
        // Show loading state
        setLoadingState(true);
        hideError();

        fetch('/api/calculate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            setLoadingState(false);
            
            if (data.success) {
                displayResults(data.data);
                resetBtn.style.display = 'block';
            } else {
                showError(data.error);
                hideResults();
            }
        })
        .catch(error => {
            setLoadingState(false);
            showError('Произошла ошибка при расчёте. Пожалуйста, попробуйте снова.');
            console.error('Error:', error);
        });
    }

    function setLoadingState(loading) {
        calculateBtn.disabled = loading;
        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            calculateBtn.classList.add('pulse');
        } else {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            calculateBtn.classList.remove('pulse');
        }
    }

    function showError(message) {
        errorBlock.textContent = message;
        errorBlock.style.display = 'block';
        errorBlock.classList.add('fade-in');
    }

    function hideError() {
        errorBlock.style.display = 'none';
        errorBlock.classList.remove('fade-in');
    }

    function hideResults() {
        resultBlock.style.display = 'none';
        resultBlock.classList.remove('fade-in');
    }

    function displayResults(data) {
        let html = '';

        // Weight gain recommendation
        if (data.weightGainRange) {
            html += `
                <div class="compact-row">
                    <span class="compact-label">Рекомендуемая прибавка:</span>
                    <span class="highlight">${data.weightGainRange}</span>
                </div>
            `;
        }

        // Conception date
        html += `
            <div class="compact-row">
                <span class="compact-label">Предполагаемая дата зачатия:</span>
                <span class="highlight">${data.conceptionDate}</span>
            </div>
        `;

        // Due date
        html += `
            <div class="compact-row">
                <span class="compact-label">Предполагаемая дата родов:</span>
                <span class="highlight">${data.dueDate}</span>
            </div>
        `;

        // Current pregnancy term
        html += `
            <div class="compact-row">
                <span class="compact-label">Текущий срок беременности:</span>
                <span class="highlight">${data.pregnancyWeeks} недель ${data.pregnancyDaysRemainder} дней</span>
            </div>
        `;

        // Days until birth
        html += `
            <div class="compact-row">
                <span class="compact-label">Дней до родов:</span>
                <span class="highlight">${data.daysUntilBirth}</span>
            </div>
        `;

        // Current trimester
        html += `
            <div class="compact-row">
                <span class="compact-label">Текущий триместр:</span>
                <span class="highlight">${data.currentTrimester}</span>
            </div>
        `;

        // Maternity leave date
        html += `
            <div class="compact-row">
                <span class="compact-label">Декретный отпуск с:</span>
                <span class="highlight">${data.maternityLeaveDate}</span>
            </div>
        `;

        // Test dates
        if (data.testDates && data.testDates.length > 0) {
            html += `
                <details>
                    <summary>Календарь анализов и обследований</summary>
                    <table class="tests-table">
            `;
            
            // Tests are already sorted by date from the backend
            data.testDates.forEach(test => {
                html += `
                    <tr>
                        <td>${test.name}</td>
                        <td><strong>${test.date}</strong></td>
                    </tr>
                `;
            });
            
            html += `
                    </table>
                </details>
            `;
        }

        // HCG levels table
        if (data.hcgLevels) {
            html += `
                <details>
                    <summary>Нормы ХГЧ по неделям беременности</summary>
                    <div class="hcg-info">
                        <p><strong>Важно:</strong> Нормы могут отличаться в разных лабораториях. Динамика роста важнее абсолютных значений.</p>
                    </div>
                    <table class="hcg-table">
                        <tr>
                            <th>Срок беременности</th>
                            <th>ХГЧ (мМЕ/мл)</th>
                        </tr>
            `;
            
            data.hcgLevels.forEach(level => {
                const currentWeekClass = level.isCurrent ? ' class="current-week"' : '';
                html += `
                    <tr${currentWeekClass}>
                        <td>${level.week === 'Небеременные' ? level.week : level.week + ' недель'}</td>
                        <td>${level.range}</td>
                    </tr>
                `;
            });
            
            html += `
                    </table>
                    <div class="hcg-note">
                        <p><small><strong>Примечания:</strong></small></p>
                        <ul>
                            <li><small>В первом триместре ХГЧ удваивается каждые 48-72 часа</small></li>
                            <li><small>Пик достигается на 8-11 неделе, затем снижается</small></li>
                            <li><small>Уровень выше 25 мМЕ/мл указывает на беременность</small></li>
                            <li><small>При уровне 1000-2000 мМЕ/мл на УЗИ видно плодное яйцо</small></li>
                        </ul>
                        <p class="hcg-source"><small><em>Источник: Российские медицинские лаборатории и клинические рекомендации</em></small></p>
                    </div>
                </details>
            `;
        }

        resultBlock.innerHTML = html;
        resultBlock.style.display = 'block';
        resultBlock.classList.add('fade-in');
    }
});
