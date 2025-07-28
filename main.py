import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import locale
from werkzeug.middleware.proxy_fix import ProxyFix


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Set Russian locale for date formatting
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU')
    except locale.Error:
        pass  # Fallback to default locale

def format_date(date_obj):
    """Format date in Russian format"""
    try:
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        return f"{date_obj.day} {months[date_obj.month - 1]} {date_obj.year} г."
    except:
        return date_obj.strftime("%d.%m.%Y")

def calculate_pregnancy_data(last_period_str, cycle_length=28, weight=None, height=None):
    """Calculate all pregnancy-related data"""
    try:
        # Parse input date
        last_period = datetime.strptime(last_period_str, '%Y-%m-%d')
        today = datetime.now()
        
        # Validate date is not in future
        if last_period > today:
            raise ValueError('Дата последней менструации не может быть в будущем.')
        
        # Calculate conception date
        ovulation_day = cycle_length - 14
        conception_date = last_period + timedelta(days=ovulation_day)
        
        # Check if conception date is in future
        if conception_date > today:
            raise ValueError('По указанным данным дата зачатия приходится на будущее. Пожалуйста, проверьте введённые данные.')
        
        # Calculate due date (280 days from last period)
        due_date = last_period + timedelta(days=280)
        
        # Calculate current pregnancy term
        pregnancy_days = (today - last_period).days
        pregnancy_weeks = pregnancy_days // 7
        pregnancy_days_remainder = pregnancy_days % 7
        
        # Calculate days until birth
        days_until_birth = (due_date - today).days
        
        # Determine current trimester
        if pregnancy_weeks <= 12:
            current_trimester = '1 триместр'
        elif pregnancy_weeks <= 27:
            current_trimester = '2 триместр'
        else:
            current_trimester = '3 триместр'
            
        # Calculate maternity leave date (30 weeks)
        maternity_leave_date = last_period + timedelta(weeks=30)
        
        # Calculate BMI and weight gain recommendation
        weight_gain_range = None
        if weight and height and height > 0:
            bmi = weight / ((height/100) ** 2)
            if bmi < 18.5:
                weight_gain_range = '12.5-18 кг'
            elif bmi < 25:
                weight_gain_range = '11.5-16 кг'
            elif bmi < 30:
                weight_gain_range = '7-11.5 кг'
            else:
                weight_gain_range = '5-9 кг'
        
        # Calculate test dates and sort by actual calendar date
        test_dates_list = [
            (11, 'Двойной тест (PAPP-A, β-ХГЧ)'),
            (12, 'УЗИ 1 триместра'),
            (16, 'Тройной тест (АФП, ХГЧ, эстриол)'),
            (20, 'УЗИ 2 триместра'),
            (24, 'Глюкозотолерантный тест'),
            (32, 'УЗИ 3 триместра'),
            (36, 'Кардиотокография (КТГ)'),
            (36, 'Посев на флору'),
            (38, 'Допплерометрия')
        ]
        
        # Create list of test dates with actual dates for sorting
        test_dates_with_dates = []
        for weeks, test_name in test_dates_list:
            actual_date = last_period + timedelta(weeks=weeks)
            test_dates_with_dates.append((actual_date, test_name))
        
        # Sort by actual calendar date
        test_dates_with_dates.sort(key=lambda x: x[0])
        
        # Create list of test dates with formatted dates for proper ordering
        test_dates = []
        for actual_date, test_name in test_dates_with_dates:
            test_dates.append({
                'name': test_name,
                'date': format_date(actual_date),
                'sortDate': actual_date.isoformat()
            })
        
        # HCG levels data (based on Russian medical standards and laboratory references)
        hcg_data = [
            {'week': 'Небеременные', 'range': '0-5,3'},
            {'week': '3-4', 'range': '16-156'},
            {'week': '4-5', 'range': '101-4 870'},
            {'week': '5-6', 'range': '1 110-31 500'},
            {'week': '6-7', 'range': '2 560-82 300'},
            {'week': '7-8', 'range': '23 100-151 000'},
            {'week': '8-9', 'range': '27 300-233 000'},
            {'week': '9-13', 'range': '20 900-291 000'},
            {'week': '13-18', 'range': '6 140-103 000'},
            {'week': '18-23', 'range': '4 720-80 100'},
            {'week': '23-41', 'range': '2 700-78 100'}
        ]
        
        # Mark current week in HCG data
        hcg_levels = []
        for hcg in hcg_data:
            is_current = False
            
            # Skip non-pregnant row for current week marking
            if hcg['week'] != 'Небеременные':
                try:
                    if '-' in hcg['week']:
                        week_range = hcg['week'].split('-')
                        start_week = int(week_range[0])
                        end_week = int(week_range[1])
                        is_current = start_week <= pregnancy_weeks <= end_week
                except (ValueError, IndexError):
                    is_current = False
            
            hcg_levels.append({
                'week': hcg['week'],
                'range': hcg['range'],
                'isCurrent': is_current
            })
        
        # Prepare response data
        response_data = {
            'conceptionDate': format_date(conception_date),
            'dueDate': format_date(due_date),
            'pregnancyWeeks': pregnancy_weeks,
            'pregnancyDaysRemainder': pregnancy_days_remainder,
            'daysUntilBirth': abs(days_until_birth),
            'currentTrimester': current_trimester,
            'maternityLeaveDate': format_date(maternity_leave_date),
            'testDates': test_dates,
            'hcgLevels': hcg_levels
        }
        
        if weight_gain_range:
            response_data['weightGainRange'] = weight_gain_range
            
        return {
            'success': True,
            'data': response_data
        }
        
    except ValueError as e:
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Произошла ошибка при расчёте. Пожалуйста, попробуйте снова.'
        }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint for pregnancy calculations"""
    try:
        # Get form data
        last_period = request.form.get('last_period')
        cycle_length = int(request.form.get('cycle_length', 28))
        weight = None
        height = None
        
        weight_str = request.form.get('pre_pregnancy_weight')
        height_str = request.form.get('height')
        
        if weight_str:
            weight = float(weight_str)
        if height_str:
            height = float(height_str)
        
        # Validate required fields
        if not last_period:
            return jsonify({
                'success': False,
                'error': 'Дата последней менструации обязательна.'
            })
        
        # Calculate pregnancy data
        result = calculate_pregnancy_data(last_period, cycle_length, weight, height)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in calculate endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при расчёте. Пожалуйста, попробуйте снова.'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
