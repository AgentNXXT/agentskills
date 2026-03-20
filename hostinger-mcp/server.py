#!/usr/bin/env python3
"""
Hostinger API MCP Server
Manage VPS, domains, DNS, billing, hosting, and email marketing via Hostinger API.
"""
import os
import re
import httpx
from mcp.server.fastmcp import FastMCP

API_KEY = os.environ.get("HOSTINGER_API_KEY", "")
BASE_URL = "https://api.hostinger.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

mcp = FastMCP("hostinger-mcp")


def _url(path: str, **kwargs) -> str:
    """Build URL with path parameter substitution."""
    for key, val in kwargs.items():
        path = path.replace(f"{{{key}}}", str(val))
    return f"{BASE_URL}{path}"


def _get(path: str, params: dict | None = None, **path_params) -> dict:
    resp = httpx.get(_url(path, **path_params), headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, json_body: dict | None = None, **path_params) -> dict:
    resp = httpx.post(_url(path, **path_params), headers=HEADERS, json=json_body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _put(path: str, json_body: dict | None = None, **path_params) -> dict:
    resp = httpx.put(_url(path, **path_params), headers=HEADERS, json=json_body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _patch(path: str, json_body: dict | None = None, **path_params) -> dict:
    resp = httpx.patch(_url(path, **path_params), headers=HEADERS, json=json_body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _delete(path: str, json_body: dict | None = None, **path_params) -> dict:
    resp = httpx.delete(_url(path, **path_params), headers=HEADERS, json=json_body, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ─── BILLING ──────────────────────────────────────────────────────────────────


@mcp.tool()
def billing_get_catalog(category: str | None = None, name: str | None = None) -> dict:
    """
    Retrieve catalog items available for order. Prices are in cents (1799 = $17.99).
    Use wildcard search with name (e.g. '.COM*'). Filter by category: DOMAIN or VPS.
    """
    params = {}
    if category:
        params["category"] = category
    if name:
        params["name"] = name
    return _get("/api/billing/v1/catalog", params=params)


@mcp.tool()
def billing_get_payment_methods() -> dict:
    """Retrieve available payment methods for placing new orders."""
    return _get("/api/billing/v1/payment-methods")


@mcp.tool()
def billing_set_default_payment_method(payment_method_id: int) -> dict:
    """Set the default payment method for your account."""
    return _post(f"/api/billing/v1/payment-methods/{payment_method_id}")


@mcp.tool()
def billing_delete_payment_method(payment_method_id: int) -> dict:
    """Delete a payment method from your account."""
    return _delete(f"/api/billing/v1/payment-methods/{payment_method_id}")


@mcp.tool()
def billing_get_subscriptions() -> dict:
    """Retrieve all subscriptions associated with your account."""
    return _get("/api/billing/v1/subscriptions")


@mcp.tool()
def billing_disable_auto_renewal(subscription_id: str) -> dict:
    """Disable auto-renewal for a subscription."""
    return _delete(f"/api/billing/v1/subscriptions/{subscription_id}/auto-renewal/disable")


@mcp.tool()
def billing_enable_auto_renewal(subscription_id: str) -> dict:
    """Enable auto-renewal for a subscription."""
    return _patch(f"/api/billing/v1/subscriptions/{subscription_id}/auto-renewal/enable")


# ─── DNS ──────────────────────────────────────────────────────────────────────


@mcp.tool()
def dns_get_records(domain: str) -> dict:
    """Retrieve DNS zone records for a specific domain."""
    return _get("/api/dns/v1/zones/{domain}", domain=domain)


@mcp.tool()
def dns_update_records(domain: str, zone: list, overwrite: bool = False) -> dict:
    """
    Update DNS records for a domain. Each zone entry needs: name, type (A/AAAA/CNAME/MX/TXT/NS/SRV/CAA/ALIAS/SOA),
    records (list of {content: str}), and optionally ttl. Use overwrite=true to replace existing records.
    """
    return _put("/api/dns/v1/zones/{domain}", json_body={"zone": zone, "overwrite": overwrite}, domain=domain)


@mcp.tool()
def dns_delete_records(domain: str) -> dict:
    """Delete DNS records for a domain. Use filters for name and type to target specific records."""
    return _delete("/api/dns/v1/zones/{domain}", domain=domain)


@mcp.tool()
def dns_validate_records(domain: str, zone: list, overwrite: bool = False) -> dict:
    """Validate DNS records before applying. Returns 200 on success or 422 on validation error."""
    return _post("/api/dns/v1/zones/{domain}/validate", json_body={"zone": zone, "overwrite": overwrite}, domain=domain)


@mcp.tool()
def dns_reset_records(domain: str, reset_email_records: bool = False, whitelisted_record_types: list | None = None) -> dict:
    """Reset DNS zone to default records. Optionally preserve specific record types."""
    body = {"domain": domain, "reset_email_records": reset_email_records}
    if whitelisted_record_types:
        body["whitelisted_record_types"] = whitelisted_record_types
    return _post("/api/dns/v1/zones/{domain}/reset", json_body=body, domain=domain)


@mcp.tool()
def dns_get_snapshots(domain: str) -> dict:
    """Retrieve DNS snapshots for a domain for backup/restoration."""
    return _get("/api/dns/v1/snapshots/{domain}", domain=domain)


@mcp.tool()
def dns_get_snapshot(domain: str, snapshot_id: int) -> dict:
    """Retrieve a specific DNS snapshot with zone record contents."""
    return _get("/api/dns/v1/snapshots/{domain}/{snapshotId}", domain=domain, snapshotId=snapshot_id)


@mcp.tool()
def dns_restore_snapshot(domain: str, snapshot_id: int) -> dict:
    """Restore DNS zone to a previous snapshot configuration."""
    return _post("/api/dns/v1/snapshots/{domain}/{snapshotId}/restore", domain=domain, snapshotId=snapshot_id)


# ─── DOMAINS ─────────────────────────────────────────────────────────────────


@mcp.tool()
def domains_check_availability(domain: str, tlds: list[str], with_alternatives: bool = False) -> dict:
    """
    Check domain availability across TLDs. Provide TLDs without dots (e.g. 'com', 'net').
    Set with_alternatives=true (single TLD only) to get suggestions. Rate limited: 10 req/min.
    """
    return _post("/api/domains/v1/availability", json_body={
        "domain": domain, "tlds": tlds, "with_alternatives": with_alternatives
    })


@mcp.tool()
def domains_get_list() -> dict:
    """Retrieve all domains in your portfolio."""
    return _get("/api/domains/v1/portfolio")


@mcp.tool()
def domains_get_details(domain: str) -> dict:
    """Retrieve detailed information for a specific domain."""
    return _get("/api/domains/v1/portfolio/{domain}", domain=domain)


@mcp.tool()
def domains_purchase(domain: str, item_id: str, payment_method_id: int | None = None, coupons: list | None = None) -> dict:
    """Purchase and register a new domain. Get item_id from billing_get_catalog(category='DOMAIN')."""
    body = {"domain": domain, "item_id": item_id}
    if payment_method_id:
        body["payment_method_id"] = payment_method_id
    if coupons:
        body["coupons"] = coupons
    return _post("/api/domains/v1/portfolio", json_body=body)


@mcp.tool()
def domains_update_nameservers(domain: str, ns1: str, ns2: str, ns3: str | None = None, ns4: str | None = None) -> dict:
    """Set nameservers for a domain. At least 2 nameservers required."""
    body = {"domain": domain, "ns1": ns1, "ns2": ns2}
    if ns3:
        body["ns3"] = ns3
    if ns4:
        body["ns4"] = ns4
    return _put("/api/domains/v1/portfolio/{domain}/nameservers", json_body=body, domain=domain)


@mcp.tool()
def domains_enable_lock(domain: str) -> dict:
    """Enable domain lock to prevent unauthorized transfers."""
    return _put("/api/domains/v1/portfolio/{domain}/domain-lock", domain=domain)


@mcp.tool()
def domains_disable_lock(domain: str) -> dict:
    """Disable domain lock to allow transfers to another registrar."""
    return _delete("/api/domains/v1/portfolio/{domain}/domain-lock", domain=domain)


@mcp.tool()
def domains_enable_privacy(domain: str) -> dict:
    """Enable privacy protection to hide owner info from public WHOIS."""
    return _put("/api/domains/v1/portfolio/{domain}/privacy-protection", domain=domain)


@mcp.tool()
def domains_disable_privacy(domain: str) -> dict:
    """Disable privacy protection to make owner info visible in WHOIS."""
    return _delete("/api/domains/v1/portfolio/{domain}/privacy-protection", domain=domain)


@mcp.tool()
def domains_create_forwarding(domain: str, redirect_url: str, redirect_type: str = "301") -> dict:
    """Create domain forwarding. redirect_type: '301' (permanent) or '302' (temporary)."""
    return _post("/api/domains/v1/forwarding", json_body={
        "domain": domain, "redirect_url": redirect_url, "redirect_type": redirect_type
    })


@mcp.tool()
def domains_get_forwarding(domain: str) -> dict:
    """Retrieve domain forwarding configuration."""
    return _get("/api/domains/v1/forwarding/{domain}", domain=domain)


@mcp.tool()
def domains_delete_forwarding(domain: str) -> dict:
    """Delete domain forwarding configuration."""
    return _delete("/api/domains/v1/forwarding/{domain}", domain=domain)


@mcp.tool()
def domains_get_whois_profiles(tld: str | None = None) -> dict:
    """Retrieve WHOIS contact profiles, optionally filtered by TLD."""
    params = {}
    if tld:
        params["tld"] = tld
    return _get("/api/domains/v1/whois", params=params)


@mcp.tool()
def domains_get_whois_profile(whois_id: int) -> dict:
    """Retrieve a specific WHOIS contact profile."""
    return _get("/api/domains/v1/whois/{whoisId}", whoisId=whois_id)


@mcp.tool()
def domains_delete_whois_profile(whois_id: int) -> dict:
    """Delete a WHOIS contact profile."""
    return _delete("/api/domains/v1/whois/{whoisId}", whoisId=whois_id)


@mcp.tool()
def domains_get_whois_profile_usage(whois_id: int) -> dict:
    """See which domains use a specific WHOIS profile."""
    return _get("/api/domains/v1/whois/{whoisId}/usage", whoisId=whois_id)


# ─── HOSTING ─────────────────────────────────────────────────────────────────


@mcp.tool()
def hosting_list_orders(page: int | None = None, per_page: int | None = None, statuses: list | None = None) -> dict:
    """Retrieve hosting orders. Filter by statuses: active, deleting, deleted, suspended."""
    params = {}
    if page:
        params["page"] = page
    if per_page:
        params["per_page"] = per_page
    if statuses:
        params["statuses"] = statuses
    return _get("/api/hosting/v1/orders", params=params)


@mcp.tool()
def hosting_list_websites(page: int | None = None, per_page: int | None = None, domain: str | None = None, order_id: int | None = None) -> dict:
    """Retrieve websites. Filter by domain name, order_id, username, or enabled status."""
    params = {}
    if page:
        params["page"] = page
    if per_page:
        params["per_page"] = per_page
    if domain:
        params["domain"] = domain
    if order_id:
        params["order_id"] = order_id
    return _get("/api/hosting/v1/websites", params=params)


@mcp.tool()
def hosting_create_website(domain: str, order_id: int, datacenter_code: str | None = None) -> dict:
    """
    Create a new website. datacenter_code is required for the first website on a new plan.
    Use hosting_list_datacenters() to see available options.
    """
    body = {"domain": domain, "order_id": order_id}
    if datacenter_code:
        body["datacenter_code"] = datacenter_code
    return _post("/api/hosting/v1/websites", json_body=body)


@mcp.tool()
def hosting_list_datacenters(order_id: int) -> dict:
    """List available datacenters for a hosting plan. First item is the best match."""
    return _get("/api/hosting/v1/datacenters", params={"order_id": order_id})


@mcp.tool()
def hosting_generate_free_subdomain() -> dict:
    """Generate a unique free *.hostingersite.com subdomain."""
    return _post("/api/hosting/v1/domains/free-subdomains")


@mcp.tool()
def hosting_verify_domain(domain: str) -> dict:
    """Verify domain ownership. If not accessible, add the returned TXT record and retry."""
    return _post("/api/hosting/v1/domains/verify-ownership", json_body={"domain": domain})


# ─── VPS ─────────────────────────────────────────────────────────────────────


@mcp.tool()
def vps_list() -> dict:
    """Retrieve all VPS instances."""
    return _get("/api/vps/v1/virtual-machines")


@mcp.tool()
def vps_get_details(vm_id: int) -> dict:
    """Retrieve detailed information about a specific VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}", virtualMachineId=vm_id)


@mcp.tool()
def vps_start(vm_id: int) -> dict:
    """Start (power on) a VPS instance."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/start", virtualMachineId=vm_id)


@mcp.tool()
def vps_stop(vm_id: int) -> dict:
    """Stop (power off) a VPS instance."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/stop", virtualMachineId=vm_id)


@mcp.tool()
def vps_restart(vm_id: int) -> dict:
    """Restart a VPS instance."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/restart", virtualMachineId=vm_id)


@mcp.tool()
def vps_recreate(vm_id: int, template_id: int, password: str | None = None, post_install_script_id: int | None = None) -> dict:
    """Reinstall OS on a VPS. WARNING: all data will be lost."""
    body = {"template_id": template_id}
    if password:
        body["password"] = password
    if post_install_script_id:
        body["post_install_script_id"] = post_install_script_id
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/recreate", json_body=body, virtualMachineId=vm_id)


@mcp.tool()
def vps_get_metrics(vm_id: int) -> dict:
    """Get performance metrics (CPU, RAM, disk, network) for a VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/metrics", virtualMachineId=vm_id)


@mcp.tool()
def vps_get_actions(vm_id: int, page: int | None = None) -> dict:
    """View operation history for a VPS."""
    params = {}
    if page:
        params["page"] = page
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/actions", params=params, virtualMachineId=vm_id)


@mcp.tool()
def vps_set_hostname(vm_id: int, hostname: str) -> dict:
    """Set hostname for a VPS. Does not auto-update PTR records."""
    return _put("/api/vps/v1/virtual-machines/{virtualMachineId}/hostname",
                json_body={"hostname": hostname}, virtualMachineId=vm_id)


@mcp.tool()
def vps_reset_hostname(vm_id: int) -> dict:
    """Reset hostname and PTR record to defaults."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/hostname", virtualMachineId=vm_id)


@mcp.tool()
def vps_set_root_password(vm_id: int, password: str) -> dict:
    """Set the root password for a VPS."""
    return _put("/api/vps/v1/virtual-machines/{virtualMachineId}/root-password",
                json_body={"password": password}, virtualMachineId=vm_id)


@mcp.tool()
def vps_set_panel_password(vm_id: int, password: str) -> dict:
    """Set the panel password for a VPS."""
    return _put("/api/vps/v1/virtual-machines/{virtualMachineId}/panel-password",
                json_body={"password": password}, virtualMachineId=vm_id)


@mcp.tool()
def vps_set_nameservers(vm_id: int, ns1: str, ns2: str | None = None) -> dict:
    """Configure DNS resolvers for a VPS."""
    body = {"ns1": ns1}
    if ns2:
        body["ns2"] = ns2
    return _put("/api/vps/v1/virtual-machines/{virtualMachineId}/nameservers",
                json_body=body, virtualMachineId=vm_id)


@mcp.tool()
def vps_create_ptr(vm_id: int, ip_address_id: int, domain: str) -> dict:
    """Create a PTR (reverse DNS) record for a VPS IP."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/ptr/{ipAddressId}",
                 json_body={"domain": domain}, virtualMachineId=vm_id, ipAddressId=ip_address_id)


@mcp.tool()
def vps_delete_ptr(vm_id: int, ip_address_id: int) -> dict:
    """Delete a PTR (reverse DNS) record."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/ptr/{ipAddressId}",
                   virtualMachineId=vm_id, ipAddressId=ip_address_id)


# ─── VPS Backups & Snapshots ────────────────────────────────────────────────


@mcp.tool()
def vps_get_backups(vm_id: int) -> dict:
    """List backups for a VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/backups", virtualMachineId=vm_id)


@mcp.tool()
def vps_restore_backup(vm_id: int, backup_id: int) -> dict:
    """Restore a VPS from backup. WARNING: all current data will be overwritten."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/backups/{backupId}/restore",
                 virtualMachineId=vm_id, backupId=backup_id)


@mcp.tool()
def vps_get_snapshot(vm_id: int) -> dict:
    """Get snapshot info for a VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/snapshot", virtualMachineId=vm_id)


@mcp.tool()
def vps_create_snapshot(vm_id: int) -> dict:
    """Create a snapshot of a VPS."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/snapshot", virtualMachineId=vm_id)


@mcp.tool()
def vps_restore_snapshot(vm_id: int) -> dict:
    """Restore a VPS from its snapshot."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/snapshot/restore", virtualMachineId=vm_id)


@mcp.tool()
def vps_delete_snapshot(vm_id: int) -> dict:
    """Delete a VPS snapshot."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/snapshot", virtualMachineId=vm_id)


@mcp.tool()
def vps_start_recovery(vm_id: int) -> dict:
    """Enable rescue/recovery mode on a VPS."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/recovery", virtualMachineId=vm_id)


@mcp.tool()
def vps_stop_recovery(vm_id: int) -> dict:
    """Exit rescue/recovery mode on a VPS."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/recovery", virtualMachineId=vm_id)


# ─── VPS SSH Keys ────────────────────────────────────────────────────────────


@mcp.tool()
def vps_get_public_keys(page: int | None = None) -> dict:
    """List SSH public keys in your account."""
    params = {}
    if page:
        params["page"] = page
    return _get("/api/vps/v1/public-keys", params=params)


@mcp.tool()
def vps_create_public_key(name: str, key: str) -> dict:
    """Add a new SSH public key to your account."""
    return _post("/api/vps/v1/public-keys", json_body={"name": name, "key": key})


@mcp.tool()
def vps_delete_public_key(key_id: int) -> dict:
    """Delete an SSH public key from your account (does not remove from VPS)."""
    return _delete("/api/vps/v1/public-keys/{publicKeyId}", publicKeyId=key_id)


@mcp.tool()
def vps_attach_keys(vm_id: int, key_ids: list[int]) -> dict:
    """Attach SSH keys to a VPS for authentication."""
    return _post("/api/vps/v1/public-keys/attach/{virtualMachineId}",
                 json_body={"ids": key_ids}, virtualMachineId=vm_id)


@mcp.tool()
def vps_get_attached_keys(vm_id: int) -> dict:
    """List SSH keys attached to a specific VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/public-keys", virtualMachineId=vm_id)


# ─── VPS Firewall ────────────────────────────────────────────────────────────


@mcp.tool()
def vps_get_firewalls(page: int | None = None) -> dict:
    """List all firewalls."""
    params = {}
    if page:
        params["page"] = page
    return _get("/api/vps/v1/firewall", params=params)


@mcp.tool()
def vps_create_firewall(name: str) -> dict:
    """Create a new firewall."""
    return _post("/api/vps/v1/firewall", json_body={"name": name})


@mcp.tool()
def vps_get_firewall(firewall_id: int) -> dict:
    """Get firewall details and rules."""
    return _get("/api/vps/v1/firewall/{firewallId}", firewallId=firewall_id)


@mcp.tool()
def vps_delete_firewall(firewall_id: int) -> dict:
    """Delete a firewall. Auto-deactivates from attached VPS."""
    return _delete("/api/vps/v1/firewall/{firewallId}", firewallId=firewall_id)


@mcp.tool()
def vps_activate_firewall(firewall_id: int, vm_id: int) -> dict:
    """Activate a firewall on a VPS. Only one firewall per VPS."""
    return _post("/api/vps/v1/firewall/{firewallId}/activate/{virtualMachineId}",
                 firewallId=firewall_id, virtualMachineId=vm_id)


@mcp.tool()
def vps_deactivate_firewall(firewall_id: int, vm_id: int) -> dict:
    """Deactivate a firewall from a VPS."""
    return _post("/api/vps/v1/firewall/{firewallId}/deactivate/{virtualMachineId}",
                 firewallId=firewall_id, virtualMachineId=vm_id)


@mcp.tool()
def vps_create_firewall_rule(firewall_id: int, protocol: str, port: str, source: str, source_detail: str) -> dict:
    """
    Add a firewall rule. By default all incoming traffic is dropped — add accept rules for needed ports.
    protocol: TCP/UDP/ICMP/SSH/HTTP/HTTPS/MySQL/PostgreSQL/any. source: 'any' or 'custom'. source_detail: IP/CIDR.
    """
    return _post("/api/vps/v1/firewall/{firewallId}/rules", json_body={
        "protocol": protocol, "port": port, "source": source, "source_detail": source_detail
    }, firewallId=firewall_id)


@mcp.tool()
def vps_update_firewall_rule(firewall_id: int, rule_id: int, protocol: str, port: str, source: str, source_detail: str) -> dict:
    """Update a firewall rule. VPS will need manual sync after changes."""
    return _put("/api/vps/v1/firewall/{firewallId}/rules/{ruleId}", json_body={
        "protocol": protocol, "port": port, "source": source, "source_detail": source_detail
    }, firewallId=firewall_id, ruleId=rule_id)


@mcp.tool()
def vps_delete_firewall_rule(firewall_id: int, rule_id: int) -> dict:
    """Delete a firewall rule."""
    return _delete("/api/vps/v1/firewall/{firewallId}/rules/{ruleId}",
                   firewallId=firewall_id, ruleId=rule_id)


@mcp.tool()
def vps_sync_firewall(firewall_id: int, vm_id: int) -> dict:
    """Sync updated firewall rules to a VPS."""
    return _post("/api/vps/v1/firewall/{firewallId}/sync/{virtualMachineId}",
                 firewallId=firewall_id, virtualMachineId=vm_id)


# ─── VPS Docker ──────────────────────────────────────────────────────────────


@mcp.tool()
def vps_docker_list_projects(vm_id: int) -> dict:
    """List all Docker Compose projects on a VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/docker", virtualMachineId=vm_id)


@mcp.tool()
def vps_docker_get_project(vm_id: int, project_name: str) -> dict:
    """Get project config, compose file contents, and status."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}",
                virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_get_containers(vm_id: int, project_name: str) -> dict:
    """List containers in a Docker project with status, ports, and stats."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/containers",
                virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_get_logs(vm_id: int, project_name: str) -> dict:
    """Get aggregated logs from all services (last 300 entries)."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/logs",
                virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_create_project(vm_id: int, project_name: str, content: str, environment: str | None = None) -> dict:
    """
    Deploy a Docker Compose project. content can be a GitHub repo URL (https://github.com/user/repo),
    a URL returning docker-compose.yaml, or raw YAML. Replaces existing project with same name.
    """
    body = {"project_name": project_name, "content": content}
    if environment:
        body["environment"] = environment
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/docker",
                 json_body=body, virtualMachineId=vm_id)


@mcp.tool()
def vps_docker_update_project(vm_id: int, project_name: str) -> dict:
    """Pull latest images and recreate containers."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/update",
                 virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_start_project(vm_id: int, project_name: str) -> dict:
    """Start all services in a Docker project."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/start",
                 virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_stop_project(vm_id: int, project_name: str) -> dict:
    """Stop all services, preserving data volumes."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/stop",
                 virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_restart_project(vm_id: int, project_name: str) -> dict:
    """Restart all services in dependency order."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/restart",
                 virtualMachineId=vm_id, projectName=project_name)


@mcp.tool()
def vps_docker_delete_project(vm_id: int, project_name: str) -> dict:
    """Remove a Docker project entirely (irreversible). Stops containers and cleans up resources."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/down",
                   virtualMachineId=vm_id, projectName=project_name)


# ─── VPS Templates & Data Centers ───────────────────────────────────────────


@mcp.tool()
def vps_get_templates() -> dict:
    """List available OS templates for VPS instances."""
    return _get("/api/vps/v1/templates")


@mcp.tool()
def vps_get_template(template_id: int) -> dict:
    """Get detailed specifications for a specific OS template."""
    return _get("/api/vps/v1/templates/{templateId}", templateId=template_id)


@mcp.tool()
def vps_get_data_centers() -> dict:
    """List all available VPS data center locations."""
    return _get("/api/vps/v1/data-centers")


# ─── VPS Post-Install Scripts ────────────────────────────────────────────────


@mcp.tool()
def vps_get_scripts(page: int | None = None) -> dict:
    """List post-install automation scripts."""
    params = {}
    if page:
        params["page"] = page
    return _get("/api/vps/v1/post-install-scripts", params=params)


@mcp.tool()
def vps_create_script(name: str, content: str) -> dict:
    """Create a post-install script (max 48KB). Runs as /post_install after VPS setup."""
    return _post("/api/vps/v1/post-install-scripts", json_body={"name": name, "content": content})


@mcp.tool()
def vps_update_script(script_id: int, name: str, content: str) -> dict:
    """Update an existing post-install script."""
    return _put("/api/vps/v1/post-install-scripts/{postInstallScriptId}",
                json_body={"name": name, "content": content}, postInstallScriptId=script_id)


@mcp.tool()
def vps_delete_script(script_id: int) -> dict:
    """Delete a post-install script."""
    return _delete("/api/vps/v1/post-install-scripts/{postInstallScriptId}", postInstallScriptId=script_id)


# ─── VPS Malware Scanner (Monarx) ───────────────────────────────────────────


@mcp.tool()
def vps_get_scan_metrics(vm_id: int) -> dict:
    """Get Monarx malware scan results for a VPS."""
    return _get("/api/vps/v1/virtual-machines/{virtualMachineId}/monarx", virtualMachineId=vm_id)


@mcp.tool()
def vps_install_monarx(vm_id: int) -> dict:
    """Install Monarx malware scanner on a VPS."""
    return _post("/api/vps/v1/virtual-machines/{virtualMachineId}/monarx", virtualMachineId=vm_id)


@mcp.tool()
def vps_uninstall_monarx(vm_id: int) -> dict:
    """Uninstall Monarx malware scanner from a VPS."""
    return _delete("/api/vps/v1/virtual-machines/{virtualMachineId}/monarx", virtualMachineId=vm_id)


# ─── EMAIL MARKETING (REACH) ────────────────────────────────────────────────


@mcp.tool()
def reach_list_contacts(group_uuid: str | None = None, subscription_status: str | None = None, page: int | None = None) -> dict:
    """List contacts. Filter by group_uuid or subscription_status (subscribed/unsubscribed)."""
    params = {}
    if group_uuid:
        params["group_uuid"] = group_uuid
    if subscription_status:
        params["subscription_status"] = subscription_status
    if page:
        params["page"] = page
    return _get("/api/reach/v1/contacts", params=params)


@mcp.tool()
def reach_create_contact(email: str, name: str | None = None, surname: str | None = None, note: str | None = None) -> dict:
    """Create a new email marketing contact. If double opt-in is enabled, confirmation email will be sent."""
    body = {"email": email}
    if name:
        body["name"] = name
    if surname:
        body["surname"] = surname
    if note:
        body["note"] = note
    return _post("/api/reach/v1/contacts", json_body=body)


@mcp.tool()
def reach_delete_contact(uuid: str) -> dict:
    """Permanently delete a contact by UUID."""
    return _delete("/api/reach/v1/contacts/{uuid}", uuid=uuid)


@mcp.tool()
def reach_list_groups() -> dict:
    """List all contact groups."""
    return _get("/api/reach/v1/contacts/groups")


@mcp.tool()
def reach_list_segments() -> dict:
    """List all contact segments."""
    return _get("/api/reach/v1/segmentation/segments")


@mcp.tool()
def reach_get_segment(segment_uuid: str) -> dict:
    """Get details of a specific segment."""
    return _get("/api/reach/v1/segmentation/segments/{segmentUuid}", segmentUuid=segment_uuid)


@mcp.tool()
def reach_list_segment_contacts(segment_uuid: str, page: int | None = None) -> dict:
    """List contacts in a segment."""
    params = {}
    if page:
        params["page"] = page
    return _get("/api/reach/v1/segmentation/segments/{segmentUuid}/contacts",
                params=params, segmentUuid=segment_uuid)


@mcp.tool()
def reach_list_profiles() -> dict:
    """List all email marketing profiles."""
    return _get("/api/reach/v1/profiles")


if __name__ == "__main__":
    mcp.run()
