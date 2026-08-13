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

def get_nutrition_recommendations(trimester):
    """Get nutrition recommendations based on trimester according to clinical guidelines"""
    recommendations = {
        1: {
            'title': 'Рекомендации по питанию в 1 триместре',
            'items': [
                'Питайтесь дробно: 5-6 раз в день небольшими порциями',
                'Употребляйте 1.5-2 литра жидкости в день (вода, морсы, компоты)',
                'Включите в рацион белковые продукты: мясо, рыбу, яйца, творог (100-120 г белка в день)',
                'Ешьте больше свежих овощей и фруктов (источники витаминов и клетчатки)',
                'Принимайте фолиевую кислоту 400 мкг/сутки для профилактики дефектов нервной трубки',
                'Избегайте сырых продуктов: суши, непастеризованного молока, сырых яиц',
                'Ограничьте кофеин до 200 мг/день (1-2 чашки кофе)',
                'Исключите алкоголь полностью'
            ]
        },
        2: {
            'title': 'Рекомендации по питанию во 2 триместре',
            'items': [
                'Увеличьте калорийность рациона на 300-350 ккал/день',
                'Потребляйте 1200-1400 мг кальция в день (молочные продукты, кунжут, рыба)',
                'Увеличьте потребление железа (красное мясо, гречка, шпинат, яблоки)',
                'Включите продукты, богатые омега-3: жирная рыба, льняное масло, грецкие орехи',
                'Контролируйте прибавку веса (оптимально 300-400 г в неделю)',
                'Ограничьте простые углеводы (сладости, выпечка) для профилактики гестационного диабета',
                'Снизьте потребление соли для профилактики отёков',
                'Продолжайте приём витаминов для беременных'
            ]
        },
        3: {
            'title': 'Рекомендации по питанию в 3 триместре',
            'items': [
                'Питайтесь часто и маленькими порциями (6-7 раз в день) для уменьшения изжоги',
                'Увеличьте калорийность на 450-500 ккал/день от добеременного рациона',
                'Потребляйте достаточно белка (120-140 г/день) для роста плода',
                'Включите продукты, богатые витамином К (зелёные листовые овощи) для свёртываемости крови',
                'Контролируйте потребление жидкости (1-1.5 л/день) для профилактики отёков',
                'Исключите продукты, вызывающие газообразование (капуста, бобовые, газировка)',
                'Употребляйте продукты, богатые цинком (мясо, орехи, цельнозерновые) для подготовки к родам',
                'За 2-3 недели до родов ограничьте легкоусвояемые углеводы и кальций'
            ]
        }
    }
    return recommendations.get(trimester, recommendations[1])

def get_vitamin_recommendations(trimester):
    """Get vitamin and supplement recommendations based on trimester"""
    recommendations = {
        1: {
            'title': 'Витамины и добавки в 1 триместре',
            'items': [
                'Фолиевая кислота: 400-800 мкг/сутки (профилактика дефектов нервной трубки)',
                'Йод: 200-250 мкг/сутки (для развития щитовидной железы плода)',
                'Витамин D: 600-800 МЕ/сутки (при дефиците — по назначению врача)',
                'Витамин B6: 1.9 мг/сутки (помогает при тошноте)',
                'Поливитамины для беременных (по рекомендации врача)'
            ],
            'note': 'В первом триместре особенно важны фолиевая кислота и йод. При выраженном токсикозе обсудите с врачом дополнительный приём витамина B6.'
        },
        2: {
            'title': 'Витамины и добавки во 2 триместре',
            'items': [
                'Железо: 27-30 мг/сутки (профилактика анемии, по показаниям)',
                'Кальций: 1000-1200 мг/сутки (формирование костей плода)',
                'Витамин D: 600-800 МЕ/сутки (усвоение кальция)',
                'Омега-3 (ДГК): 200-300 мг/сутки (развитие мозга и зрения)',
                'Магний: 350-400 мг/сутки (при судорогах и повышенном тонусе)',
                'Продолжение приёма фолиевой кислоты и йода'
            ],
            'note': 'Во втором триместре возрастает потребность в железе и кальции. Препараты железа лучше принимать отдельно от кальция и чая.'
        },
        3: {
            'title': 'Витамины и добавки в 3 триместре',
            'items': [
                'Железо: 27-30 мг/сутки (поддержание уровня гемоглобина)',
                'Кальций: 1000-1200 мг/сутки (минерализация костей)',
                'Витамин K: 90 мкг/сутки (подготовка к родам, свёртываемость)',
                'Витамин C: 85 мг/сутки (укрепление сосудов, иммунитет)',
                'Омега-3 (ДГК): 200-300 мг/сутки (развитие мозга)',
                'Пробиотики (по показаниям, для профилактики дисбиоза)'
            ],
            'note': 'В третьем триместре важно поддерживать уровень железа и кальция. За 2-3 недели до родов обсудите с врачом необходимость отмены некоторых добавок.'
        }
    }
    return recommendations.get(trimester, recommendations[1])

def get_doctor_visits_schedule(trimester):
    """Get doctor visit schedule based on trimester according to Russian clinical guidelines"""
    schedule = {
        1: {
            'title': 'Посещения врачей в 1 триместре',
            'visits': [
                {'week': '6-8 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Постановка на учёт, подтверждение беременности, осмотр'},
                {'week': '8-12 недель', 'doctor': 'Терапевт', 'description': 'Консультация, ЭКГ, оценка общего здоровья'},
                {'week': '8-12 недель', 'doctor': 'Офтальмолог', 'description': 'Осмотр глазного дна, оценка состояния сетчатки'},
                {'week': '8-12 недель', 'doctor': 'Стоматолог', 'description': 'Санация полости рта, лечение кариеса'},
                {'week': '8-12 недель', 'doctor': 'ЛОР', 'description': 'Консультация при наличии хронических заболеваний'},
                {'week': '10-12 недель', 'doctor': 'Эндокринолог', 'description': 'По показаниям (заболевания щитовидной железы, диабет)'},
                {'week': '11-13 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Скрининг 1 триместра, УЗИ, двойной тест'}
            ],
            'frequency': 'В 1 триместре посещение акушера-гинеколога — 1 раз в месяц'
        },
        2: {
            'title': 'Посещения врачей во 2 триместре',
            'visits': [
                {'week': '16-18 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Плановый осмотр, скрининг 2 триместра (тройной тест)'},
                {'week': '18-21 неделя', 'doctor': 'Акушер-гинеколог', 'description': 'УЗИ 2 триместра (анатомическое исследование)'},
                {'week': '20-24 недели', 'doctor': 'Акушер-гинеколог', 'description': 'Оценка результатов скрининга, измерение живота'},
                {'week': '24-28 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Глюкозотолерантный тест (скрининг гестационного диабета)'},
                {'week': '26-28 недель', 'doctor': 'Терапевт', 'description': 'Повторная консультация при наличии показаний'}
            ],
            'frequency': 'Во 2 триместре посещение акушера-гинеколога — 1 раз в 2-3 недели'
        },
        3: {
            'title': 'Посещения врачей в 3 триместре',
            'visits': [
                {'week': '30 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Оформление декретного отпуска, обследование перед отпуском'},
                {'week': '30-32 недели', 'doctor': 'Акушер-гинеколог', 'description': 'УЗИ 3 триместра, оценка положения плода'},
                {'week': '32-34 недели', 'doctor': 'Акушер-гинеколог', 'description': 'Плановый осмотр, КТГ по показаниям'},
                {'week': '36 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Осмотр, посев на флору, начало еженедельных визитов'},
                {'week': '36-40 недель', 'doctor': 'Акушер-гинеколог', 'description': 'Еженедельные осмотры, КТГ, оценка готовности к родам'}
            ],
            'frequency': 'В 3 триместре посещение акушера-гинеколога — 1 раз в 2 недели до 36 недели, затем еженедельно'
        }
    }
    return schedule.get(trimester, schedule[1])

def calculate_pregnancy_data(last_period_str, cycle_length=28, weight=None, height=None):
    """Calculate all pregnancy-related data with clinical recommendations"""
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
            trimester_num = 1
        elif pregnancy_weeks <= 27:
            current_trimester = '2 триместр'
            trimester_num = 2
        else:
            current_trimester = '3 триместр'
            trimester_num = 3
            
        # Calculate maternity leave date (30 weeks)
        maternity_leave_date = last_period + timedelta(weeks=30)
        
        # Calculate BMI and weight gain recommendation
        weight_gain_range = None
        bmi = None
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
        
        # Calculate test dates and sort by actual calendar date - Extended with clinical recommendations
        test_dates_list = [
            # 1 триместр
            (4, 'Анализ крови на ХГЧ для подтверждения беременности'),
            (6, 'УЗИ для подтверждения маточной беременности и сердцебиения'),
            (8, 'Посещение акушера-гинеколога (постановка на учёт)'),
            (10, 'Развёрнутый анализ крови, группа крови, резус-фактор'),
            (11, 'Двойной тест (PAPP-A, β-ХГЧ) - пренатальный скрининг 1 триместра'),
            (12, 'УЗИ 1 триместра (скрининговое)'),
            (12, 'ЭКГ при постановке на учёт'),
            (12, 'Консультация терапевта'),
            (12, 'Консультация окулиста'),
            (12, 'Консультация стоматолога'),
            (12, 'Консультация ЛОРа'),
            # 2 триместр
            (16, 'Тройной тест (АФП, ХГЧ, эстриол) - пренатальный скрининг 2 триместра'),
            (18, 'Посещение акушера-гинеколога'),
            (20, 'УЗИ 2 триместра (скрининговое, определение пола при желании)'),
            (24, 'Глюкозотолерантный тест (скрининг гестационного диабета)'),
            (24, 'Общий анализ мочи'),
            (26, 'Посещение акушера-гинеколога'),
            (28, 'Анализ крови на антитела (при отрицательном резус-факторе)'),
            # 3 триместр
            (30, 'Посещение акушера-гинеколога (оформление декретного отпуска)'),
            (30, 'Развёрнутый анализ крови, коагулограмма'),
            (30, 'Анализ на ВИЧ, сифилис, гепатиты B и C'),
            (32, 'УЗИ 3 триместра (скрининговое, оценка положения плода)'),
            (32, 'КТГ (кардиотокография) - по показаниям'),
            (34, 'Посещение акушера-гинеколога'),
            (36, 'Кардиотокография (КТГ)'),
            (36, 'Посев на флору'),
            (36, 'Посещение акушера-гинеколога (еженедельно с этого срока)'),
            (38, 'Допплерометрия (оценка кровотока)'),
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
            'hcgLevels': hcg_levels,
            'nutritionRecommendations': get_nutrition_recommendations(trimester_num),
            'vitaminRecommendations': get_vitamin_recommendations(trimester_num),
            'doctorVisits': get_doctor_visits_schedule(trimester_num)
        }
        
        if weight_gain_range:
            response_data['weightGainRange'] = weight_gain_range
        if bmi:
            response_data['bmi'] = round(bmi, 1)
            
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
