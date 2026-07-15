/**
 * TP-Link Deco card — a Lovelace custom card that lists the clients connected to
 * the TP-Link Deco mesh exposed by the `tplink_deco` integration, showing each
 * client's connection state, address and live throughput.
 *
 * Zero-build vanilla web component (no Lit/bundler). Styles are driven entirely
 * by Home Assistant design tokens so the card follows the active theme and
 * light/dark mode automatically. The layout mirrors the "IP tiles" look of the
 * built-in Internet dashboard: a rounded icon badge, a name, a secondary line
 * and a trailing status.
 *
 * Clients are discovered from the entity registry: every device that owns a
 * `tplink_deco` device_tracker entity is a client, and its companion entities
 * (IP, MAC, connection type, download/upload, connected) are matched by their
 * integration translation keys — so discovery is language independent.
 *
 * Config:
 *   type: custom:tplink-deco-card
 *   devices: [...]                # optional: device ids to show. when omitted,
 *                                 #   every Deco client is shown.
 *   secondary_info: ip            # ip | mac | connection | none (default ip)
 *   sort: name                    # name | download | upload | connection (default name)
 *   columns: 2                    # max columns (1-6, default 2); wraps down on
 *                                 #   narrow widths so it stays responsive
 *   show_offline: true            # include disconnected clients (default true)
 */

const DEFAULT_SECONDARY = "ip";
const DEFAULT_SORT = "name";
const DEFAULT_COLUMNS = 2;
const MAX_COLUMNS = 6;
const MIN_COLUMN_WIDTH = "240px";
const SECONDARY_OPTIONS = ["ip", "mac", "connection", "none"];
const SORT_OPTIONS = ["name", "download", "upload", "connection"];

const CONNECTION_ICONS = {
  wired: "mdi:ethernet",
  band2_4: "mdi:wifi",
  band5: "mdi:wifi",
  band6: "mdi:wifi",
};

const CONNECTION_LABELS = {
  wired: "Wired",
  band2_4: "2.4 GHz",
  band5: "5 GHz",
  band6: "6 GHz",
};

// i18n — pure frontend plugin (no custom_component translations), so strings are
// embedded here and picked by the active HA UI language, falling back to English.
const TRANSLATIONS = {
  en: {
    "card.empty": "No TP-Link Deco clients found",
    "card.offline": "Offline",
    "card.title": "Devices",
    "conn.wired": "Wired",
    "conn.band2_4": "2.4 GHz",
    "conn.band5": "5 GHz",
    "conn.band6": "6 GHz",
    "editor.devices": "Clients to show (leave empty for all)",
    "editor.secondary": "Secondary info",
    "editor.secondary_ip": "IP address",
    "editor.secondary_mac": "MAC address",
    "editor.secondary_connection": "Connection type",
    "editor.secondary_none": "None",
    "editor.sort": "Sort by",
    "editor.sort_name": "Name",
    "editor.sort_download": "Download speed",
    "editor.sort_upload": "Upload speed",
    "editor.sort_connection": "Connection type",
    "editor.columns": "Maximum columns",
    "editor.show_offline": "Show offline clients",
  },
  "pt-BR": {
    "card.empty": "Nenhum cliente TP-Link Deco encontrado",
    "card.offline": "Offline",
    "card.title": "Dispositivos",
    "conn.wired": "Cabo",
    "conn.band2_4": "2,4 GHz",
    "conn.band5": "5 GHz",
    "conn.band6": "6 GHz",
    "editor.devices": "Clientes a exibir (vazio = todos)",
    "editor.secondary": "Informação secundária",
    "editor.secondary_ip": "Endereço IP",
    "editor.secondary_mac": "Endereço MAC",
    "editor.secondary_connection": "Tipo de conexão",
    "editor.secondary_none": "Nenhuma",
    "editor.sort": "Ordenar por",
    "editor.sort_name": "Nome",
    "editor.sort_download": "Velocidade de download",
    "editor.sort_upload": "Velocidade de upload",
    "editor.sort_connection": "Tipo de conexão",
    "editor.columns": "Máximo de colunas",
    "editor.show_offline": "Mostrar clientes offline",
  },
};

const EDITOR_LABEL_KEYS = {
  devices: "editor.devices",
  secondary_info: "editor.secondary",
  sort: "editor.sort",
  columns: "editor.columns",
  show_offline: "editor.show_offline",
};

/** The active HA UI language, or a supported fallback (base lang, then "en"). */
function resolveLang(hass) {
  const lang = (hass && (hass.locale?.language || hass.language || hass.selectedLanguage)) || "en";
  if (TRANSLATIONS[lang]) return lang;
  if (lang.split("-")[0] === "pt") return "pt-BR";
  return "en";
}

/** Translate a dotted key for the active language; English is the fallback. */
function localize(hass, key) {
  const lang = resolveLang(hass);
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en[key] ?? key;
}

/** Escape a string for safe interpolation into innerHTML. */
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

/** Human-readable connection label for a raw connection_type state. */
function connectionLabel(hass, value) {
  const key = `conn.${value}`;
  const translated = TRANSLATIONS[resolveLang(hass)]?.[key];
  if (translated) return translated;
  return CONNECTION_LABELS[value] ?? value ?? "";
}

/** Format a throughput sensor state ("12.3" + "Mbit/s") into a compact string. */
function formatSpeed(state) {
  if (!state || state.state === "unavailable" || state.state === "unknown") return null;
  const value = Number(state.state);
  if (!Number.isFinite(value)) return null;
  const unit = state.attributes?.unit_of_measurement ?? "";
  const rounded = value >= 100 ? Math.round(value) : Math.round(value * 10) / 10;
  return `${rounded} ${unit}`.trim();
}

class TpLinkDecoCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._signature = null;
  }

  static getConfigElement() {
    return document.createElement("tplink-deco-card-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:tplink-deco-card",
      secondary_info: DEFAULT_SECONDARY,
      sort: DEFAULT_SORT,
      columns: DEFAULT_COLUMNS,
      show_offline: true,
    };
  }

  setConfig(config) {
    const secondary = config.secondary_info ?? DEFAULT_SECONDARY;
    if (!SECONDARY_OPTIONS.includes(secondary)) {
      throw new Error(`tplink-deco-card: "secondary_info" must be one of ${SECONDARY_OPTIONS.join(", ")}`);
    }
    const sort = config.sort ?? DEFAULT_SORT;
    if (!SORT_OPTIONS.includes(sort)) {
      throw new Error(`tplink-deco-card: "sort" must be one of ${SORT_OPTIONS.join(", ")}`);
    }
    const devices =
      Array.isArray(config.devices) && config.devices.length ? config.devices.slice() : null;
    const columns = Number.parseInt(config.columns, 10);
    this._config = {
      secondaryInfo: secondary,
      sort,
      columns: Number.isFinite(columns) ? Math.min(MAX_COLUMNS, Math.max(1, columns)) : DEFAULT_COLUMNS,
      showOffline: config.show_offline ?? true,
      devices,
    };
    this._signature = null;
    if (this._hass) this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 4;
  }

  getGridOptions() {
    return { min_columns: 12, min_rows: 3 };
  }

  /**
   * Discover Deco client devices from the entity registry.
   *
   * Every tplink_deco device that owns a device_tracker entity is a client;
   * companion entities are matched by their integration translation keys.
   */
  _collect() {
    const hass = this._hass;
    const entities = hass.entities || {};
    const devices = hass.devices || {};

    const byDevice = {};
    for (const entry of Object.values(entities)) {
      if (entry.platform !== "tplink_deco" || !entry.device_id) continue;
      (byDevice[entry.device_id] ??= []).push(entry);
    }

    const wanted = this._config.devices ? new Set(this._config.devices) : null;
    const items = [];

    for (const [deviceId, list] of Object.entries(byDevice)) {
      if (wanted && !wanted.has(deviceId)) continue;

      const tracker = list.find((e) => e.entity_id.startsWith("device_tracker."));
      if (!tracker) continue;

      const byKey = {};
      for (const e of list) {
        if (e.translation_key) byKey[e.translation_key] = e.entity_id;
      }

      const device = devices[deviceId] || {};
      const trackerState = hass.states[tracker.entity_id];
      const connectedState = byKey.connected ? hass.states[byKey.connected] : null;
      const online =
        trackerState?.state === "home" || connectedState?.state === "on";

      const connectionState = byKey.connection_type ? hass.states[byKey.connection_type] : null;
      const connectionType = connectionState?.state;
      const ipState = byKey.ip ? hass.states[byKey.ip] : null;
      const macState = byKey.mac ? hass.states[byKey.mac] : null;
      const downloadState = byKey.download ? hass.states[byKey.download] : null;
      const uploadState = byKey.upload ? hass.states[byKey.upload] : null;

      items.push({
        deviceId,
        moreInfoEntity: byKey.ip || tracker.entity_id,
        name:
          device.name_by_user ||
          device.name ||
          trackerState?.attributes?.friendly_name ||
          tracker.entity_id,
        online,
        connectionType,
        ip: ipState && ["unavailable", "unknown"].includes(ipState.state) ? null : ipState?.state,
        mac: macState && ["unavailable", "unknown"].includes(macState.state) ? null : macState?.state,
        download: formatSpeed(downloadState),
        upload: formatSpeed(uploadState),
        downloadValue: Number(downloadState?.state) || 0,
        uploadValue: Number(uploadState?.state) || 0,
      });
    }

    const filtered = this._config.showOffline ? items : items.filter((i) => i.online);
    const collator = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });
    filtered.sort((a, b) => {
      if (a.online !== b.online) return a.online ? -1 : 1;
      switch (this._config.sort) {
        case "download":
          return b.downloadValue - a.downloadValue;
        case "upload":
          return b.uploadValue - a.uploadValue;
        case "connection":
          return collator.compare(a.connectionType || "", b.connectionType || "");
        default:
          return collator.compare(a.name, b.name);
      }
    });
    return filtered;
  }

  _render() {
    if (!this._hass) return;
    const hass = this._hass;
    const t = (key) => localize(hass, key);
    const lang = resolveLang(hass);
    const items = this._collect();
    const secondary = this._config.secondaryInfo;

    const signature = JSON.stringify([
      lang,
      secondary,
      this._config.sort,
      this._config.columns,
      this._config.showOffline,
      items.map((i) => [i.deviceId, i.online, i.connectionType, i.ip, i.mac, i.download, i.upload]),
    ]);
    if (signature === this._signature) return;
    this._signature = signature;

    const rows = items
      .map((item) => {
        const icon = item.online
          ? CONNECTION_ICONS[item.connectionType] || "mdi:lan-connect"
          : "mdi:wifi-off";

        let secondaryText = "";
        if (secondary === "ip") secondaryText = item.ip || "—";
        else if (secondary === "mac") secondaryText = item.mac || "—";
        else if (secondary === "connection")
          secondaryText = item.online ? connectionLabel(hass, item.connectionType) : t("card.offline");

        const secondaryHtml =
          secondary === "none" ? "" : `<div class="secondary">${esc(secondaryText)}</div>`;

        const trailing = item.online
          ? `<div class="stats">
               <span class="stat"><ha-icon icon="mdi:arrow-down"></ha-icon>${esc(item.download || "—")}</span>
               <span class="stat"><ha-icon icon="mdi:arrow-up"></ha-icon>${esc(item.upload || "—")}</span>
             </div>`
          : `<div class="offline">${esc(t("card.offline"))}</div>`;

        return `
          <ha-card class="item ${item.online ? "" : "is-offline"}" data-entity="${esc(item.moreInfoEntity)}">
            <div class="row">
              <div class="badge">
                <ha-icon icon="${esc(icon)}"></ha-icon>
              </div>
              <div class="body">
                <div class="name">${esc(item.name)}</div>
                ${secondaryHtml}
              </div>
              ${trailing}
            </div>
            <ha-ripple></ha-ripple>
          </ha-card>`;
      })
      .join("");

    const empty = `<ha-card class="empty-card"><div class="empty"><ha-icon icon="mdi:router-wireless-off"></ha-icon><span>${t("card.empty")}</span></div></ha-card>`;

    this.shadowRoot.innerHTML = `
      <style>${TpLinkDecoCard.styles}</style>
      <div class="grid" style="--cols:${this._config.columns}">${items.length ? rows : empty}</div>`;

    this.shadowRoot.querySelectorAll(".item").forEach((item) => {
      item.addEventListener("click", () => this._showMore(item.dataset.entity));
    });
  }

  /** Open the more-info dialog for an entity (standard HA behaviour). */
  _showMore(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true })
    );
  }

  static get styles() {
    return `
      :host { display: block; }
      .grid {
        --cols: 1;
        --gap: 8px;
        display: grid;
        gap: var(--gap);
        grid-template-columns: repeat(
          auto-fill,
          minmax(max(${MIN_COLUMN_WIDTH}, calc((100% - (var(--cols) - 1) * var(--gap)) / var(--cols))), 1fr)
        );
      }
      .item {
        position: relative;
        overflow: hidden;
        cursor: pointer;
        --ha-ripple-color: var(--primary-color);
      }
      .item.is-offline { opacity: 0.55; }
      .row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 10px 12px;
        min-height: 44px;
      }
      .badge {
        flex: 0 0 auto;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: color-mix(in srgb, var(--primary-color) 18%, transparent);
        color: var(--primary-color);
      }
      .item.is-offline .badge {
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }
      .badge ha-icon { --mdc-icon-size: 22px; }
      .body { flex: 1 1 auto; min-width: 0; }
      .name {
        color: var(--primary-text-color);
        font-size: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .secondary {
        color: var(--secondary-text-color);
        font-size: 0.8125rem;
        margin-top: 2px;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .stats {
        flex: 0 0 auto;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
      }
      .stat {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        color: var(--secondary-text-color);
        font-size: 0.8125rem;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
      }
      .stat ha-icon { --mdc-icon-size: 15px; }
      .offline {
        flex: 0 0 auto;
        color: var(--secondary-text-color);
        font-size: 0.85rem;
      }
      .empty-card { grid-column: 1 / -1; }
      .empty {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--secondary-text-color);
        padding: 16px 12px;
      }
    `;
  }
}

class TpLinkDecoCardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _schema() {
    const t = (key) => localize(this._hass, key);
    return [
      {
        name: "devices",
        selector: {
          device: {
            multiple: true,
            filter: { integration: "tplink_deco" },
          },
        },
      },
      {
        name: "secondary_info",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "ip", label: t("editor.secondary_ip") },
              { value: "mac", label: t("editor.secondary_mac") },
              { value: "connection", label: t("editor.secondary_connection") },
              { value: "none", label: t("editor.secondary_none") },
            ],
          },
        },
      },
      {
        name: "sort",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "name", label: t("editor.sort_name") },
              { value: "download", label: t("editor.sort_download") },
              { value: "upload", label: t("editor.sort_upload") },
              { value: "connection", label: t("editor.sort_connection") },
            ],
          },
        },
      },
      {
        name: "columns",
        selector: { number: { min: 1, max: MAX_COLUMNS, mode: "box" } },
      },
      { name: "show_offline", selector: { boolean: {} } },
    ];
  }

  _labels(schema) {
    return localize(this._hass, EDITOR_LABEL_KEYS[schema.name] ?? schema.name);
  }

  _render() {
    if (!this._hass) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) => this._labels(schema);
      this._form.addEventListener("value-changed", (ev) => {
        const config = { type: "custom:tplink-deco-card", ...ev.detail.value };
        this.dispatchEvent(
          new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true })
        );
      });
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = {
      devices: this._config.devices ?? [],
      secondary_info: this._config.secondary_info ?? DEFAULT_SECONDARY,
      sort: this._config.sort ?? DEFAULT_SORT,
      columns: this._config.columns ?? DEFAULT_COLUMNS,
      show_offline: this._config.show_offline ?? true,
    };
  }
}

// The module runs once per URL it is served from, and the card URL carries the
// integration version. Upgrading the integration without restarting Home
// Assistant leaves the previous version's URL registered alongside the new one,
// so the module is evaluated twice. Without this guard the second run throws on
// the already-taken tag name and registers a duplicate card picker entry.
if (!customElements.get("tplink-deco-card")) {
  customElements.define("tplink-deco-card", TpLinkDecoCard);
  customElements.define("tplink-deco-card-editor", TpLinkDecoCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "tplink-deco-card",
    name: "TP-Link Deco Card",
    description: "Lists the clients connected to the TP-Link Deco mesh with their address and throughput.",
    preview: true,
    documentationURL: "https://github.com/roquerodrigo/ha-tplink-deco",
  });

  // eslint-disable-next-line no-console
  console.info("%c tplink-deco-card ", "background:#4ABC96;color:#fff;border-radius:3px", "loaded");
}
