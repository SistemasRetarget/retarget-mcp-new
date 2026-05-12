"""
Validador Mobile First y Responsive Design.
Verifica cumplimiento con estándares de Google para desarrollo mobile-first.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List

class MobileFirstValidator:
    """
    Valida que un sitio siga principios Mobile First y responsive design.
    
    Estándares Google:
    - Viewport correctamente configurado
    - Touch targets >= 48x48px
    - Media queries mobile-first (min-width)
    - Responsive images (srcset)
    - Font sizes legibles (16px base)
    - No horizontal scroll
    - Tap targets no overlap
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
    
    def validate(self, url: str) -> Dict[str, Any]:
        """
        Valida Mobile First de una URL.
        
        Returns:
            Dict con resultados de validación mobile-first
        """
        results = {
            'url': url,
            'passed': True,
            'score': 0,
            'max_score': 100,
            'checks': {},
            'issues': [],
            'recommendations': [],
            'mobile_first_compliant': False
        }
        
        try:
            # Obtener página como mobile
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parsear HTML y CSS
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = response.text
            
            # 1. Viewport Configuration
            viewport_check = self._check_viewport(soup)
            results['checks']['viewport'] = viewport_check
            results['score'] += viewport_check.get('score', 0)
            if not viewport_check['passed']:
                results['passed'] = False
                results['issues'].append("Viewport no configurado correctamente para mobile")
            
            # 2. Media Queries Mobile-First
            media_check = self._check_media_queries(html_content)
            results['checks']['media_queries'] = media_check
            results['score'] += media_check.get('score', 0)
            if not media_check['passed']:
                results['recommendations'].append("Usar approach mobile-first (min-width en lugar de max-width)")
            
            # 3. Responsive Images
            images_check = self._check_responsive_images(soup)
            results['checks']['responsive_images'] = images_check
            results['score'] += images_check.get('score', 0)
            if not images_check['passed']:
                results['recommendations'].append("Agregar srcset y sizes a imágenes para responsive")
            
            # 4. Font Sizes Legibles
            font_check = self._check_font_sizes(soup, html_content)
            results['checks']['font_sizes'] = font_check
            results['score'] += font_check.get('score', 0)
            if not font_check['passed']:
                results['issues'].append("Font size base menor a 16px (puede causar zoom en iOS)")
            
            # 5. Touch Targets
            touch_check = self._check_touch_targets(soup, html_content)
            results['checks']['touch_targets'] = touch_check
            results['score'] += touch_check.get('score', 0)
            if not touch_check['passed']:
                results['issues'].append(f"{touch_check.get('small_targets', 0)} elementos con touch target < 48x48px")
            
            # 6. No Horizontal Scroll
            scroll_check = self._check_horizontal_scroll(soup, html_content)
            results['checks']['horizontal_scroll'] = scroll_check
            results['score'] += scroll_check.get('score', 0)
            if not scroll_check['passed']:
                results['issues'].append("Posible scroll horizontal detectado (overflow-x)")
            
            # 7. Flexible Layout (Flexbox/Grid)
            layout_check = self._check_flexible_layout(html_content)
            results['checks']['flexible_layout'] = layout_check
            results['score'] += layout_check.get('score', 0)
            if not layout_check['passed']:
                results['recommendations'].append("Usar CSS Flexbox o Grid en lugar de floats/fixed widths")
            
            # 8. Input Zoom Prevention
            zoom_check = self._check_input_zoom(soup, html_content)
            results['checks']['input_zoom'] = zoom_check
            results['score'] += zoom_check.get('score', 0)
            if not zoom_check['passed']:
                results['recommendations'].append("Inputs con font-size < 16px causan zoom en iOS")
            
            # Determinar cumplimiento mobile-first
            results['mobile_first_compliant'] = results['score'] >= 80 and results['passed']
            
            return results
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'passed': False,
                'mobile_first_compliant': False,
                'score': 0
            }
    
    def _check_viewport(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica viewport correctamente configurado."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        if not viewport:
            return {'passed': False, 'score': 0, 'detail': 'No viewport meta tag'}
        
        content = viewport.get('content', '')
        
        # Verificar componentes esenciales
        has_width = 'width=device-width' in content
        has_initial_scale = 'initial-scale=1' in content
        
        if has_width and has_initial_scale:
            return {
                'passed': True,
                'score': 15,
                'detail': f'Viewport correcto: {content}'
            }
        elif has_width:
            return {
                'passed': True,
                'score': 10,
                'detail': f'Viewport parcial (falta initial-scale): {content}'
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'Viewport incompleto: {content}'
            }
    
    def _check_media_queries(self, css_content: str) -> Dict[str, Any]:
        """Verifica uso de media queries mobile-first."""
        # Buscar media queries
        media_queries = re.findall(r'@media\s+([^\{]+)', css_content)
        
        if not media_queries:
            return {'passed': False, 'score': 0, 'detail': 'No media queries encontradas'}
        
        # Contar min-width vs max-width
        min_width_count = sum(1 for mq in media_queries if 'min-width' in mq)
        max_width_count = sum(1 for mq in media_queries if 'max-width' in mq)
        
        # Mobile-first prefere min-width
        if min_width_count > max_width_count:
            return {
                'passed': True,
                'score': 15,
                'detail': f'Approach mobile-first: {min_width_count} min-width, {max_width_count} max-width'
            }
        elif max_width_count > 0:
            return {
                'passed': False,
                'score': 5,
                'detail': f'Desktop-first detectado: {max_width_count} max-width vs {min_width_count} min-width'
            }
        else:
            return {
                'passed': True,
                'score': 10,
                'detail': f'Media queries encontradas: {len(media_queries)}'
            }
    
    def _check_responsive_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica que imágenes sean responsive."""
        images = soup.find_all('img')
        
        if not images:
            return {'passed': True, 'score': 10, 'detail': 'No images to check'}
        
        responsive_count = 0
        for img in images:
            if img.get('srcset') or img.get('sizes'):
                responsive_count += 1
        
        percentage = (responsive_count / len(images)) * 100
        
        if percentage >= 80:
            return {
                'passed': True,
                'score': 10,
                'detail': f'{percentage:.0f}% imágenes con srcset/sizes'
            }
        elif percentage >= 50:
            return {
                'passed': True,
                'score': 5,
                'detail': f'{percentage:.0f}% imágenes responsive (mejorable)'
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'Solo {percentage:.0f}% imágenes responsive'
            }
    
    def _check_font_sizes(self, soup: BeautifulSoup, css_content: str) -> Dict[str, Any]:
        """Verifica font sizes legibles en mobile."""
        # Buscar font-size base
        base_font = re.search(r'html\s*\{[^}]*font-size:\s*(\d+)px', css_content)
        body_font = re.search(r'body\s*\{[^}]*font-size:\s*(\d+)px', css_content)
        
        base_size = 16  # default
        if base_font:
            base_size = int(base_font.group(1))
        elif body_font:
            base_size = int(body_font.group(1))
        
        if base_size >= 16:
            return {
                'passed': True,
                'score': 10,
                'detail': f'Font size base: {base_size}px (✓ legible)'
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'Font size base: {base_size}px (✗ muy pequeño)'
            }
    
    def _check_touch_targets(self, soup: BeautifulSoup, css_content: str) -> Dict[str, Any]:
        """Verifica touch targets de al menos 48x48px."""
        # Buscar elementos clickeables con tamaño pequeño
        small_targets = []
        
        # Buscar en CSS: width/height < 48px en elementos interactivos
        button_patterns = [
            r'(?:button|a|\.btn|\[role=["\']button["\']\])\s*\{[^}]*(?:width|min-width):\s*(\d+)px[^}]*(?:height|min-height):\s*(\d+)px',
            r'(?:width|min-width):\s*(\d+)px[^}]*(?:height|min-height):\s*(\d+)px[^}]*(?:button|a|\.btn)'
        ]
        
        for pattern in button_patterns:
            matches = re.findall(pattern, css_content, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    width, height = int(match[0]), int(match[1])
                    if width < 48 or height < 48:
                        small_targets.append({'width': width, 'height': height})
        
        if not small_targets:
            return {'passed': True, 'score': 10, 'detail': 'Touch targets >= 48x48px'}
        
        if len(small_targets) <= 3:
            return {
                'passed': True,
                'score': 5,
                'detail': f'{len(small_targets)} elementos < 48x48px (aceptable)',
                'small_targets': len(small_targets)
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'{len(small_targets)} elementos < 48x48px',
                'small_targets': len(small_targets)
            }
    
    def _check_horizontal_scroll(self, soup: BeautifulSoup, css_content: str) -> Dict[str, Any]:
        """Detecta posible scroll horizontal."""
        # Buscar overflow-x o widths > 100vw
        overflow_issues = []
        
        # Buscar overflow-x: scroll o hidden mal configurado
        if re.search(r'overflow-x:\s*scroll', css_content):
            overflow_issues.append('overflow-x: scroll detectado')
        
        # Buscar elementos con width: 100vw o mayor
        vw_pattern = r'width:\s*(\d+)vw'
        vw_matches = re.findall(vw_pattern, css_content)
        for vw in vw_matches:
            if int(vw) > 100:
                overflow_issues.append(f'Width {vw}vw > 100vw')
        
        if not overflow_issues:
            return {'passed': True, 'score': 10, 'detail': 'No horizontal scroll detectado'}
        elif len(overflow_issues) <= 2:
            return {
                'passed': True,
                'score': 5,
                'detail': f'Posibles issues: {", ".join(overflow_issues[:2])}'
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'Scroll horizontal probable: {len(overflow_issues)} issues'
            }
    
    def _check_flexible_layout(self, css_content: str) -> Dict[str, Any]:
        """Verifica uso de Flexbox o Grid en lugar de floats."""
        has_flexbox = 'display: flex' in css_content or 'display:flex' in css_content
        has_grid = 'display: grid' in css_content or 'display:grid' in css_content
        has_float = 'float: ' in css_content and 'float: none' not in css_content
        
        modern_layout = has_flexbox or has_grid
        
        if modern_layout and not has_float:
            return {
                'passed': True,
                'score': 10,
                'detail': f'✓ Flexbox: {has_flexbox}, Grid: {has_grid}, Sin floats'
            }
        elif modern_layout and has_float:
            return {
                'passed': True,
                'score': 5,
                'detail': 'Usa Flexbox/Grid pero aún tiene floats (migrar gradualmente)'
            }
        elif has_float:
            return {
                'passed': False,
                'score': 0,
                'detail': 'Usa floats (legacy) - migrar a Flexbox/Grid'
            }
        else:
            return {'passed': True, 'score': 5, 'detail': 'No layout methods detectados'}
    
    def _check_input_zoom(self, soup: BeautifulSoup, css_content: str) -> Dict[str, Any]:
        """Verifica que inputs no causen zoom en iOS."""
        # Buscar input font-size < 16px
        input_font_pattern = r'(?:input|textarea|select)\s*\{[^}]*font-size:\s*(\d+)px'
        matches = re.findall(input_font_pattern, css_content, re.IGNORECASE)
        
        small_inputs = [size for size in matches if int(size) < 16]
        
        if not small_inputs:
            return {
                'passed': True,
                'score': 10,
                'detail': 'Inputs con font-size >= 16px (no zoom en iOS)'
            }
        else:
            return {
                'passed': False,
                'score': 0,
                'detail': f'{len(small_inputs)} inputs con font-size < 16px (causan zoom)'
            }


def validate_mobile_first(url: str) -> Dict[str, Any]:
    """Función de conveniencia."""
    validator = MobileFirstValidator()
    return validator.validate(url)
