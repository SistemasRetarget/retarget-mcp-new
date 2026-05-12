"""
Validador de Core Web Vitals para sitios web.
Usa PageSpeed Insights API para validar métricas de rendimiento.
"""

import requests
import json
from typing import Dict, Any, Tuple

class CoreWebVitalsValidator:
    """
    Valida Core Web Vitals de un sitio web.
    
    Métricas:
    - LCP (Largest Contentful Paint): < 2.5s
    - INP (Interaction to Next Paint): < 200ms  
    - CLS (Cumulative Layout Shift): < 0.1
    - TTFB (Time to First Byte): < 600ms
    - FCP (First Contentful Paint): < 1.8s
    """
    
    # Umbrales según Google
    THRESHOLDS = {
        'LCP': {'good': 2500, 'poor': 4000},  # ms
        'INP': {'good': 200, 'poor': 500},    # ms
        'CLS': {'good': 0.1, 'poor': 0.25},   # unitless
        'TTFB': {'good': 600, 'poor': 1000},  # ms
        'FCP': {'good': 1800, 'poor': 3000},  # ms
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def validate(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        """
        Valida Core Web Vitals de una URL.
        
        Args:
            url: URL del sitio a validar
            strategy: "mobile" o "desktop"
            
        Returns:
            Dict con resultados de validación
        """
        try:
            # Llamar a PageSpeed Insights API
            params = {
                'url': url,
                'strategy': strategy,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extraer métricas
            lighthouse = data.get('lighthouseResult', {})
            metrics = lighthouse.get('audits', {})
            
            results = {
                'url': url,
                'strategy': strategy,
                'overall_score': lighthouse.get('categories', {}).get('PERFORMANCE', {}).get('score', 0) * 100,
                'metrics': {},
                'passed': True,
                'issues': []
            }
            
            # Validar cada métrica
            for metric_name, thresholds in self.THRESHOLDS.items():
                metric_data = self._get_metric_value(metrics, metric_name)
                value = metric_data.get('value', 0)
                display_value = metric_data.get('displayValue', f"{value}")
                
                # Determinar status
                if value <= thresholds['good']:
                    status = 'good'
                elif value <= thresholds['poor']:
                    status = 'needs_improvement'
                else:
                    status = 'poor'
                
                results['metrics'][metric_name] = {
                    'value': value,
                    'display_value': display_value,
                    'status': status,
                    'threshold_good': thresholds['good'],
                    'threshold_poor': thresholds['poor']
                }
                
                # Si es poor, falla la validación
                if status == 'poor':
                    results['passed'] = False
                    results['issues'].append(f"{metric_name}: {display_value} (poor)")
            
            return results
            
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'error': f"Error conectando con PageSpeed Insights: {str(e)}",
                'passed': False,
                'metrics': {}
            }
        except Exception as e:
            return {
                'url': url,
                'error': f"Error inesperado: {str(e)}",
                'passed': False,
                'metrics': {}
            }
    
    def _get_metric_value(self, metrics: Dict, metric_name: str) -> Dict:
        """Extrae el valor de una métrica específica."""
        mapping = {
            'LCP': 'largest-contentful-paint',
            'INP': 'interaction-to-next-paint',
            'CLS': 'cumulative-layout-shift',
            'TTFB': 'server-response-time',
            'FCP': 'first-contentful-paint'
        }
        
        audit_id = mapping.get(metric_name, metric_name.lower())
        metric = metrics.get(audit_id, {})
        
        return {
            'value': metric.get('numericValue', 0),
            'displayValue': metric.get('displayValue', 'N/A'),
            'score': metric.get('score', 0)
        }
    
    def get_summary(self, results: Dict[str, Any]) -> str:
        """Genera un resumen legible de los resultados."""
        if 'error' in results:
            return f"❌ Error: {results['error']}"
        
        summary = [f"Core Web Vitals - {results['url']}"]
        summary.append(f"Overall Score: {results['overall_score']:.0f}/100")
        summary.append("")
        
        for metric, data in results['metrics'].items():
            emoji = '🟢' if data['status'] == 'good' else '🟡' if data['status'] == 'needs_improvement' else '🔴'
            summary.append(f"{emoji} {metric}: {data['display_value']} ({data['status']})")
        
        summary.append("")
        summary.append(f"Resultado: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
        
        return "\n".join(summary)


# Función de conveniencia para uso directo
def validate_core_web_vitals(url: str, api_key: str = None) -> Dict[str, Any]:
    """
    Valida Core Web Vitals de una URL.
    
    Uso:
        results = validate_core_web_vitals("https://example.com")
        print(results['passed'])  # True/False
    """
    validator = CoreWebVitalsValidator(api_key)
    return validator.validate(url)
