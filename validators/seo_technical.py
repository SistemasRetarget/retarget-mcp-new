"""
Validador SEO técnico para sitios web.
Verifica elementos SEO esenciales para indexación y ranking.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class SEOTechnicalValidator:
    """
    Valida SEO técnico de un sitio web.
    
    Verifica:
    - Meta title y description presentes
    - Schema.org markup
    - Canonical URL
    - Sitemap.xml accesible
    - Robots.txt accesible
    - Heading structure (H1, H2)
    - Alt text en imágenes
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SEOBot/1.0)'
        })
    
    def validate(self, url: str) -> Dict[str, Any]:
        """
        Valida SEO técnico de una URL.
        """
        results = {
            'url': url,
            'passed': True,
            'checks': {},
            'score': 0,
            'max_score': 100,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Obtener página principal
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Meta Title
            title_check = self._check_meta_title(soup)
            results['checks']['meta_title'] = title_check
            results['score'] += title_check.get('score', 0)
            if not title_check['passed']:
                results['issues'].append("Meta title ausente o muy corto")
            
            # 2. Meta Description
            desc_check = self._check_meta_description(soup)
            results['checks']['meta_description'] = desc_check
            results['score'] += desc_check.get('score', 0)
            if not desc_check['passed']:
                results['issues'].append("Meta description ausente o muy corta")
            
            # 3. Canonical URL
            canonical_check = self._check_canonical(soup, url)
            results['checks']['canonical'] = canonical_check
            results['score'] += canonical_check.get('score', 0)
            if not canonical_check['passed']:
                results['issues'].append("Canonical URL no configurada")
            
            # 4. Heading Structure
            heading_check = self._check_headings(soup)
            results['checks']['headings'] = heading_check
            results['score'] += heading_check.get('score', 0)
            if not heading_check['passed']:
                results['issues'].append("Estructura de headings incorrecta")
            
            # 5. Alt Text en imágenes
            alt_check = self._check_image_alts(soup)
            results['checks']['image_alts'] = alt_check
            results['score'] += alt_check.get('score', 0)
            if not alt_check['passed']:
                results['recommendations'].append(f"{alt_check['missing_count']} imágenes sin alt text")
            
            # 6. Schema.org markup
            schema_check = self._check_schema_markup(soup)
            results['checks']['schema_markup'] = schema_check
            results['score'] += schema_check.get('score', 0)
            if not schema_check['passed']:
                results['recommendations'].append("Agregar Schema.org markup")
            
            # 7. Verificar sitemap.xml
            sitemap_check = self._check_sitemap(url)
            results['checks']['sitemap'] = sitemap_check
            results['score'] += sitemap_check.get('score', 0)
            if not sitemap_check['passed']:
                results['recommendations'].append("Crear y configurar sitemap.xml")
            
            # 8. Verificar robots.txt
            robots_check = self._check_robots_txt(url)
            results['checks']['robots_txt'] = robots_check
            results['score'] += robots_check.get('score', 0)
            
            # Determinar si pasó (score >= 70)
            results['passed'] = results['score'] >= 70
            
            return results
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'passed': False,
                'score': 0
            }
    
    def _check_meta_title(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica meta title."""
        title = soup.find('title')
        if not title:
            return {'passed': False, 'score': 0, 'detail': 'No title tag'}
        
        title_text = title.get_text().strip()
        length = len(title_text)
        
        if 30 <= length <= 60:
            return {'passed': True, 'score': 15, 'detail': f'Perfecto: {length} caracteres', 'value': title_text}
        elif 10 <= length < 30:
            return {'passed': True, 'score': 10, 'detail': f'Corto: {length} caracteres', 'value': title_text}
        else:
            return {'passed': False, 'score': 5, 'detail': f'Muy largo o corto: {length} caracteres', 'value': title_text}
    
    def _check_meta_description(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica meta description."""
        desc = soup.find('meta', attrs={'name': 'description'})
        if not desc:
            desc = soup.find('meta', attrs={'property': 'og:description'})
        
        if not desc:
            return {'passed': False, 'score': 0, 'detail': 'No meta description'}
        
        content = desc.get('content', '').strip()
        length = len(content)
        
        if 120 <= length <= 160:
            return {'passed': True, 'score': 15, 'detail': f'Perfecto: {length} caracteres', 'value': content}
        elif 50 <= length < 120:
            return {'passed': True, 'score': 10, 'detail': f'Corto: {length} caracteres', 'value': content}
        else:
            return {'passed': False, 'score': 5, 'detail': f'Muy largo o corto: {length} caracteres', 'value': content}
    
    def _check_canonical(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Verifica canonical URL."""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            return {'passed': True, 'score': 10, 'detail': f'Canonical: {canonical.get("href")}'}
        return {'passed': False, 'score': 0, 'detail': 'No canonical URL'}
    
    def _check_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica estructura de headings."""
        h1s = soup.find_all('h1')
        h2s = soup.find_all('h2')
        
        if len(h1s) == 0:
            return {'passed': False, 'score': 0, 'detail': 'No H1 encontrado'}
        elif len(h1s) > 1:
            return {'passed': False, 'score': 5, 'detail': f'Múltiples H1 ({len(h1s)}), debería haber 1'}
        
        if len(h2s) == 0:
            return {'passed': True, 'score': 10, 'detail': '1 H1, pero no H2s (recomendable agregar)'}
        
        return {'passed': True, 'score': 15, 'detail': f'Perfecto: 1 H1, {len(h2s)} H2s'}
    
    def _check_image_alts(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica alt text en imágenes."""
        images = soup.find_all('img')
        total = len(images)
        
        if total == 0:
            return {'passed': True, 'score': 10, 'detail': 'No images on page'}
        
        missing_alt = [img for img in images if not img.get('alt')]
        missing_count = len(missing_alt)
        
        if missing_count == 0:
            return {'passed': True, 'score': 10, 'detail': f'All {total} images have alt text'}
        
        percentage = (missing_count / total) * 100
        if percentage < 20:
            return {'passed': True, 'score': 5, 'detail': f'{missing_count}/{total} missing alt', 'missing_count': missing_count}
        else:
            return {'passed': False, 'score': 0, 'detail': f'{missing_count}/{total} missing alt', 'missing_count': missing_count}
    
    def _check_schema_markup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Verifica Schema.org markup."""
        schemas = soup.find_all('script', type='application/ld+json')
        
        if schemas:
            return {'passed': True, 'score': 10, 'detail': f'{len(schemas)} Schema.org script(s) found'}
        return {'passed': False, 'score': 0, 'detail': 'No Schema.org markup found'}
    
    def _check_sitemap(self, base_url: str) -> Dict[str, Any]:
        """Verifica sitemap.xml."""
        try:
            sitemap_url = base_url.rstrip('/') + '/sitemap.xml'
            response = self.session.head(sitemap_url, timeout=10)
            if response.status_code == 200:
                return {'passed': True, 'score': 10, 'detail': 'sitemap.xml found'}
            return {'passed': False, 'score': 0, 'detail': 'sitemap.xml not found'}
        except:
            return {'passed': False, 'score': 0, 'detail': 'Could not check sitemap'}
    
    def _check_robots_txt(self, base_url: str) -> Dict[str, Any]:
        """Verifica robots.txt."""
        try:
            robots_url = base_url.rstrip('/') + '/robots.txt'
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                return {'passed': True, 'score': 5, 'detail': 'robots.txt found'}
            return {'passed': False, 'score': 0, 'detail': 'robots.txt not found'}
        except:
            return {'passed': False, 'score': 0, 'detail': 'Could not check robots.txt'}


def validate_seo_technical(url: str) -> Dict[str, Any]:
    """Función de conveniencia."""
    validator = SEOTechnicalValidator()
    return validator.validate(url)
