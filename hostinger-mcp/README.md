# Hostinger API MCP Server

A Python MCP server that exposes the full Hostinger API as tools for Claude. Manage VPS instances, domains, DNS, billing, hosting, and email marketing — all from your AI assistant.

## Prerequisites

- Python 3.12+
- Docker (optional)
- [Hostinger API key](https://hpanel.hostinger.com) — go to Profile → Account Information → API → Generate token

## Quick Start (Local)

```bash
pip install -r requirements.txt
export HOSTINGER_API_KEY=your_key_here
python server.py
```

## Quick Start (Docker)

```bash
export HOSTINGER_API_KEY=your_key_here
docker-compose up --build
```

## Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hostinger": {
      "command": "python",
      "args": ["/path/to/hostinger-mcp/server.py"],
      "env": {
        "HOSTINGER_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Tools (78 total)

### Billing (7 tools)

| Tool | Description |
|------|-------------|
| `billing_get_catalog` | Browse products and pricing (prices in cents) |
| `billing_get_payment_methods` | List payment methods |
| `billing_set_default_payment_method` | Set default payment |
| `billing_delete_payment_method` | Remove payment method |
| `billing_get_subscriptions` | List all subscriptions |
| `billing_disable_auto_renewal` | Turn off auto-renewal |
| `billing_enable_auto_renewal` | Turn on auto-renewal |

### DNS (8 tools)

| Tool | Description |
|------|-------------|
| `dns_get_records` | View zone records |
| `dns_update_records` | Modify DNS records |
| `dns_delete_records` | Remove DNS records |
| `dns_validate_records` | Validate before applying |
| `dns_reset_records` | Restore defaults |
| `dns_get_snapshots` | List DNS backups |
| `dns_get_snapshot` | View specific backup |
| `dns_restore_snapshot` | Revert DNS config |

### Domains (16 tools)

| Tool | Description |
|------|-------------|
| `domains_check_availability` | Check domain availability across TLDs |
| `domains_get_list` | View domain portfolio |
| `domains_get_details` | Get domain info |
| `domains_purchase` | Register a new domain |
| `domains_update_nameservers` | Set nameservers |
| `domains_enable_lock` / `domains_disable_lock` | Transfer lock |
| `domains_enable_privacy` / `domains_disable_privacy` | WHOIS privacy |
| `domains_create_forwarding` / `domains_get_forwarding` / `domains_delete_forwarding` | Domain redirects |
| `domains_get_whois_profiles` / `domains_get_whois_profile` / `domains_delete_whois_profile` | WHOIS contacts |
| `domains_get_whois_profile_usage` | See where profiles are used |

### Hosting (6 tools)

| Tool | Description |
|------|-------------|
| `hosting_list_orders` | View hosting orders |
| `hosting_list_websites` | List websites |
| `hosting_create_website` | Create new website |
| `hosting_list_datacenters` | View datacenter options |
| `hosting_generate_free_subdomain` | Get free *.hostingersite.com subdomain |
| `hosting_verify_domain` | Verify domain ownership |

### VPS (38 tools)

**Instance Management:** `vps_list`, `vps_get_details`, `vps_start`, `vps_stop`, `vps_restart`, `vps_recreate`, `vps_get_metrics`, `vps_get_actions`, `vps_set_hostname`, `vps_reset_hostname`, `vps_set_root_password`, `vps_set_panel_password`, `vps_set_nameservers`, `vps_create_ptr`, `vps_delete_ptr`

**Backups & Snapshots:** `vps_get_backups`, `vps_restore_backup`, `vps_get_snapshot`, `vps_create_snapshot`, `vps_restore_snapshot`, `vps_delete_snapshot`, `vps_start_recovery`, `vps_stop_recovery`

**SSH Keys:** `vps_get_public_keys`, `vps_create_public_key`, `vps_delete_public_key`, `vps_attach_keys`, `vps_get_attached_keys`

**Firewall:** `vps_get_firewalls`, `vps_create_firewall`, `vps_get_firewall`, `vps_delete_firewall`, `vps_activate_firewall`, `vps_deactivate_firewall`, `vps_create_firewall_rule`, `vps_update_firewall_rule`, `vps_delete_firewall_rule`, `vps_sync_firewall`

**Docker:** `vps_docker_list_projects`, `vps_docker_get_project`, `vps_docker_get_containers`, `vps_docker_get_logs`, `vps_docker_create_project`, `vps_docker_update_project`, `vps_docker_start_project`, `vps_docker_stop_project`, `vps_docker_restart_project`, `vps_docker_delete_project`

**Templates & Scripts:** `vps_get_templates`, `vps_get_template`, `vps_get_data_centers`, `vps_get_scripts`, `vps_create_script`, `vps_update_script`, `vps_delete_script`

**Security:** `vps_get_scan_metrics`, `vps_install_monarx`, `vps_uninstall_monarx`

### Email Marketing / Reach (8 tools)

| Tool | Description |
|------|-------------|
| `reach_list_contacts` | List contacts with filters |
| `reach_create_contact` | Add new contact |
| `reach_delete_contact` | Remove contact |
| `reach_list_groups` | View contact groups |
| `reach_list_segments` | View segments |
| `reach_get_segment` | Get segment details |
| `reach_list_segment_contacts` | List contacts in segment |
| `reach_list_profiles` | View email profiles |

## Running Tests

```bash
pip install pytest
pytest test_server.py -v
```

## Environment Variable

| Variable | Required | Description |
|----------|----------|-------------|
| `HOSTINGER_API_KEY` | Yes | Bearer token from hPanel → Profile → API |

## License

Apache-2.0
