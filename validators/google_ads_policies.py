"""
Validador de políticas de Google Ads para landing pages.
Verifica que un sitio cumpla con los requisitos para anunciar en Google Ads.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re

class GoogleAdsPolicyValidator:
    """
    Valida que una landing page cumpla con políticas de Google Ads.
    
    Requisitos:
    - Política de privacidad visible
    - No contenido engañoso
    - No pop-ups intrusivos
    - Mobile-friendly
    - HTTPS obligatorio
    - Contacto claro
    - No malware/software no deseado
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate(self, url: str) -> Dict[str, Any]:
        """
        Valida políticas de Google Ads de una URL.
        
        Args:
            url: URL de la landing page
            
        Returns:
            Dict con resultados de validación
        """
        results = {
            'url': url,
            'passed': True,
            'checks': {},
            'issues': [],
            'warnings': []
        }
        
        try:
            # Verificar HTTPS
            https_check = self._check_https(url)
            results['checks']['https'] = https_check
            if not https_check['passed']:
                results['passed'] = False
                results['issues'].append("El sitio no usa HTTPS (obligatorio para Google Ads)")
            
            # Obtener contenido de la página
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = response.text.lower()
            
            # Verificar política de privacidad
            privacy_check = self._check_privacy_policy(soup, html_content)
            results['checks']['privacy_policy'] = privacy_check
            if not privacy_check['passed']:
                results['passed'] = False
                results['issues'].append("No se encontró política de privacidad visible")
            
            # Verificar contacto claro
            contact_check = self._check_contact_info(soup, html_content)
            results['checks']['contact_info'] = contact_check
            if not contact_check['passed']:
                results['warnings'].append("Información de contacto no encontrada o poco visible")
            
            # Verificar mobile-friendly (viewport)
            mobile_check = self._check_mobile_friendly(soup)
            results['checks']['mobile_friendly'] = mobile_check
            if not mobile_check['passed']:
                results['passed'] = False
                results['issues'].append("El sitio no es mobile-friendly (viewport no configurado)")
            
            # Verificar pop-ups intrusivos
            popup_check = self._check_intrusive_popups(soup)
            results['checks']['intrusive_popups'] = popup_check
            if not popup_check['passed']:
                results['warnings'].append("Posibles pop-ups intrusivos detectados")
            
            # Verificar contenido engañoso (básico)
            misleading_check = self._check_misleading_content(html_content)
            results['checks']['misleading_content'] = misleading_check
            if not misleading_check['passed']:
                results['passed'] = False
                results['issues'].append("Posible contenido engañoso detectado")
            
            return results
            
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'error': f"Error accediendo al sitio: {str(e)}",
                'passed': False,
                'checks': {}
            }
        except Exception as e:
            return {
                'url': url,
                'error': f"Error inesperado: {str(e)}",
                'passed': False,
                'checks': {}
            }
    
    def _check_https(self, url: str) -> Dict[str, Any]:
        """Verifica si el sitio usa HTTPS."""
        return {
            'passed': url.startswith('https://'),
            'detail': 'HTTPS habilitado' if url.startswith('https://') else 'HTTPS no detectado'
        }
    
    def _check_privacy_policy(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Verifica si hay política de privacidad visible."""
        privacy_keywords = ['política de privacidad', 'privacy policy', 'privacidad', 'privacy']
        
        # Buscar en enlaces
        for link in soup.find_all('a'):
            link_text = link.get_text().lower()
            if any(keyword in link_text for keyword in privacy_keywords):
                return {'passed': True, 'detail': f'Enlace encontrado: {link_text.strip()}'}
        
        # Buscar en footer
        footer = soup.find('footer')
        if footer:
            footer_text = footer.get_text().lower()
            if any(keyword in footer_text for keyword in privacy_keywords):
                return {'passed': True, 'detail': 'Mención en footer'}
        
        # Buscar en todo el HTML
        if any(keyword in html_content for keyword in privacy_keywords):
            return {'passed': True, 'detail': 'Mención encontrada en página'}
        
        return {'passed': False, 'detail': 'No se encontró política de privacidad'}
    
    def _check_contact_info(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Verifica si hay información de contacto clara."""
        contact_patterns = [
            r'[\w\.-]+@[\w\.-]+\.\w+',  # Email
            r'\+?\d[\d\s-]{7,}\d',       # Teléfono
        ]
        
        for pattern in contact_patterns:
            if re.search(pattern, html_content):
                return {'passed': True, 'detail': 'Información de contacto encontrada'}
        
        contact_keywords = ['contacto', 'contact', 'escríbenos', 'escribenos', 'llámanos']
        for link in soup.find_all('a'):
            if any(keyword in link.get_text().lower() for keyword in contact_keywords):
                return {'passed': True, 'detail': 'Página de contacto encontrada'}
        
        return {'passed': False, 'detail': 'No se encontró información de contacto clara'}
    
    def _check_mobile_friendly(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica si tiene viewport configurado (básico para mobile-friendly)."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            return {'passed': True, 'detail': f'Viewport: {viewport.get("content", "")}'}
        return {'passed': False, 'detail': 'Viewport no configurado'}
    
    def _check_intrusive_popups(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detecta posibles pop-ups intrusivos."""
        popup_indicators = ['modal', 'overlay', 'popup', 'lightbox']
        
        suspicious_elements = []
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', [])).lower()
            if any(indicator in classes for indicator in popup_indicators):
                suspicious_elements.append(classes)
        
        if len(suspicious_elements) > 2:
            return {
                'passed': False,
                'detail': f'{len(suspicious_elements)} elementos de modal/popup detectados'
            }
        
        return {'passed': True, 'detail': 'No se detectaron pop-ups intrusivos obvios'}
    
    def _check_misleading_content(self, html_content: str) -> Dict[str, Any]:
        """Verifica contenido posiblemente engañoso."""
        misleading_phrases = [
            'ganar dinero fácil',
            'dinero rápido',
            'truco secreto',
            '100% garantizado',
            'sin riesgo',
            'click aquí ahora',
            'oferta limitada!!!',
            'gratis!!!',
        ]
        
        found_phrases = []
        for phrase in misleading_phrases:
            if phrase in html_content:
                found_phrases.append(phrase)
        
        if found_phrases:
            return {
                'passed': False,
                'detail': f'Frases potencialmente engañosas: {", ".join(found_phrases)}'
            }
        
        return {'passed': True, 'detail': 'No se detectó contenido engañoso obvio'}


# Función de conveniencia
def validate_google_ads_policies(url: str) -> Dict[str, Any]:
    """
    Valida políticas de Google Ads de una URL.
    
    Uso:
        results = validate_google_ads_policies("https://example.com")
        print(results['passed'])  # True/False
    """
    validator = GoogleAdsPolicyValidator()
    return validator.validate(url)
