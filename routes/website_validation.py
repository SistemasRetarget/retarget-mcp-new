"""
Endpoint API para validación completa de sitios web.
Integra Core Web Vitals, políticas Google Ads y SEO técnico.
"""

from flask import Blueprint, request, jsonify
from validators.core_web_vitals import validate_core_web_vitals
from validators.google_ads_policies import validate_google_ads_policies
from validators.seo_technical import validate_seo_technical
from validators.mobile_first import validate_mobile_first
import os

website_validation_bp = Blueprint('website_validation', __name__, url_prefix='/api/v1')


@website_validation_bp.route('/validate-website', methods=['POST'])
def validate_website():
    """
    Valida un sitio web completo.
    
    Body JSON:
        {
            "url": "https://example.com/landing",
            "strategy": "mobile"  // opcional, default: "mobile"
        }
    
    Returns:
        {
            "url": "https://example.com/landing",
            "passed": true/false,
            "overall_score": 85,
            "core_web_vitals": { ... },
            "google_ads_policies": { ... },
            "seo_technical": { ... },
            "issues": [...],
            "recommendations": [...]
        }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL requerida. Ejemplo: {"url": "https://example.com"}'
            }), 400
        
        url = data['url']
        strategy = data.get('strategy', 'mobile')
        
        # Validar URL
        if not url.startswith('http://') and not url.startswith('https://'):
            return jsonify({
                'error': 'URL debe comenzar con http:// o https://'
            }), 400
        
        # Ejecutar validaciones
        results = {
            'url': url,
            'passed': True,
            'overall_score': 0,
            'core_web_vitals': {},
            'google_ads_policies': {},
            'seo_technical': {},
            'issues': [],
            'recommendations': []
        }
        
        # 1. Core Web Vitals
        cwv_results = validate_core_web_vitals(url, api_key=os.getenv('PAGESPEED_API_KEY'))
        results['core_web_vitals'] = cwv_results
        
        if not cwv_results.get('passed', False):
            results['passed'] = False
        if 'issues' in cwv_results:
            results['issues'].extend(cwv_results['issues'])
        
        # 2. Google Ads Policies
        ads_results = validate_google_ads_policies(url)
        results['google_ads_policies'] = ads_results
        
        if not ads_results.get('passed', False):
            results['passed'] = False
        if 'issues' in ads_results:
            results['issues'].extend(ads_results['issues'])
        if 'warnings' in ads_results:
            results['recommendations'].extend(ads_results['warnings'])
        
        # 3. SEO Técnico
        seo_results = validate_seo_technical(url)
        results['seo_technical'] = seo_results
        
        if not seo_results.get('passed', False):
            results['passed'] = False
        if 'issues' in seo_results:
            results['issues'].extend(seo_results['issues'])
        if 'recommendations' in seo_results:
            results['recommendations'].extend(seo_results['recommendations'])
        
        # 4. Mobile First & Responsive Design
        mobile_results = validate_mobile_first(url)
        results['mobile_first'] = mobile_results
        
        if not mobile_results.get('passed', False):
            results['passed'] = False
        if 'issues' in mobile_results:
            results['issues'].extend(mobile_results['issues'])
        if 'recommendations' in mobile_results:
            results['recommendations'].extend(mobile_results['recommendations'])
        
        # Calcular score general (promedio ponderado)
        scores = []
        if 'overall_score' in cwv_results:
            scores.append(cwv_results['overall_score'] * 0.25)  # 25% CWV
        if seo_results.get('score'):
            scores.append(seo_results['score'] * 0.25)  # 25% SEO
        if mobile_results.get('score'):
            scores.append(mobile_results['score'] * 0.25)  # 25% Mobile First
        if ads_results.get('passed'):
            scores.append(100 * 0.25)  # 25% Ads (binario)
        else:
            scores.append(0 * 0.25)
        
        results['overall_score'] = round(sum(scores)) if scores else 0
        results['mobile_first_compliant'] = mobile_results.get('mobile_first_compliant', False)
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error interno: {str(e)}'
        }), 500


@website_validation_bp.route('/validate-website/quick', methods=['GET'])
def validate_website_quick():
    """
    Validación rápida vía query params.
    
    Query params:
        url: URL del sitio a validar
        
    Ejemplo:
        GET /api/v1/validate-website/quick?url=https://example.com
    """
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'Parámetro url requerido'}), 400
    
    # Ejecutar validaciones básicas
    results = {
        'url': url,
        'quick_check': True,
        'passed': True
    }
    
    # Solo validar políticas de Google Ads (más rápido)
    ads_results = validate_google_ads_policies(url)
    results['google_ads_policies'] = {
        'passed': ads_results.get('passed', False),
        'checks': ads_results.get('checks', {})
    }
    results['passed'] = ads_results.get('passed', False)
    
    return jsonify(results), 200


@website_validation_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'website-validation',
        'version': '1.0.0'
    }), 200
