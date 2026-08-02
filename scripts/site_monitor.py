#!/usr/bin/env python3
"""Website uptime and SSL monitor for OpenClaw ops assessment.

Checks:
- HTTP status code (200 = UP, anything else = DOWN)
- Response time (WARN if > 5s)
- SSL certificate expiry (WARN if < 14 days, CRITICAL if < 7 days)
- DNS resolution

Outputs structured results for cron consumption.
"""

import sys
import json
import time
import ssl
import socket
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone

SITES = [
    {"name": "aitoolalliance", "url": "https://www.aitoolalliance.com"},
    {"name": "aibusinessinsider", "url": "https://www.aibusinessinsider.org"},
    {"name": "aicofounderstack", "url": "https://www.aicofounderstack.com"},
]

TIMEOUT = 15
SLOW_THRESHOLD = 5.0
SSL_WARN_DAYS = 14
SSL_CRIT_DAYS = 7


def check_ssl_expiry(hostname, port=443):
    """Check SSL certificate expiry days."""
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
        conn.settimeout(10)
        conn.connect((hostname, port))
        cert = conn.getpeercert()
        conn.close()

        expiry_str = cert['notAfter']
        expiry = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
        expiry = expiry.replace(tzinfo=timezone.utc)
        days_left = (expiry - datetime.now(timezone.utc)).days
        return days_left, None
    except Exception as e:
        return None, str(e)


def check_site(site):
    """Check a single site's uptime, response time, and SSL."""
    url = site['url']
    hostname = url.replace('https://', '').replace('http://', '').split('/')[0]
    result = {
        'name': site['name'],
        'url': url,
        'up': False,
        'status': None,
        'response_time': None,
        'ssl_days_left': None,
        'ssl_error': None,
        'dns_ok': False,
        'error': None,
    }

    # DNS check
    try:
        socket.getaddrinfo(hostname, None)
        result['dns_ok'] = True
    except socket.gaierror as e:
        result['error'] = f'DNS resolution failed: {e}'
        return result

    # SSL check
    ssl_days = check_ssl_expiry(hostname)
    if isinstance(ssl_days, tuple):
        result['ssl_days_left'] = None
        result['ssl_error'] = ssl_days[1]
    else:
        result['ssl_days_left'] = ssl_days

    # HTTP check
    try:
        req = Request(url, headers={'User-Agent': 'Nova-Ops-Monitor/1.0'})
        start = time.time()
        resp = urlopen(req, timeout=TIMEOUT)
        elapsed = time.time() - start
        result['status'] = resp.status
        result['up'] = resp.status == 200
        result['response_time'] = round(elapsed, 2)
    except HTTPError as e:
        result['status'] = e.code
        result['up'] = False
        result['error'] = f'HTTP {e.code}: {e.reason}'
    except URLError as e:
        result['up'] = False
        result['error'] = f'URL Error: {e.reason}'
    except Exception as e:
        result['up'] = False
        result['error'] = str(e)

    return result


def format_report(results):
    """Format results into a concise report."""
    lines = []
    alerts = []

    for r in results:
        status_icon = 'UP' if r['up'] else 'DOWN'
        line = f"  {r['name']}: {status_icon}"
        if r['status']:
            line += f" (HTTP {r['status']})"
        if r['response_time'] is not None:
            line += f" ({r['response_time']}s)"
            if r['response_time'] > SLOW_THRESHOLD:
                line += ' SLOW'
                alerts.append(f"WARNING: {r['name']} response time {r['response_time']}s > {SLOW_THRESHOLD}s")
        if r['error']:
            line += f" [{r['error']}]"
        lines.append(line)

        # SSL alerts
        if r['ssl_days_left'] is not None:
            if r['ssl_days_left'] < SSL_CRIT_DAYS:
                alerts.append(f"CRITICAL: {r['name']} SSL cert expires in {r['ssl_days_left']} days")
            elif r['ssl_days_left'] < SSL_WARN_DAYS:
                alerts.append(f"WARNING: {r['name']} SSL cert expires in {r['ssl_days_left']} days")

        if not r['dns_ok']:
            alerts.append(f"CRITICAL: {r['name']} DNS resolution failed")

    report = "## Website Uptime\n"
    report += '\n'.join(lines) + '\n'

    if alerts:
        report += '\n## Alerts\n'
        report += '\n'.join(f'- {a}' for a in alerts)
    else:
        report += '\nNo alerts.'

    return report


def main():
    results = [check_site(site) for site in SITES]
    report = format_report(results)

    if '--json' in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        print(report)

    # Exit code: 1 if any site is DOWN or SSL critical
    any_down = any(not r['up'] for r in results)
    ssl_critical = any(
        r['ssl_days_left'] is not None and r['ssl_days_left'] < SSL_CRIT_DAYS
        for r in results
    )
    if any_down or ssl_critical:
        sys.exit(1)


if __name__ == '__main__':
    main()