const CARD_TYPE = "tplink-deco-card";
const EDITOR_TYPE = "tplink-deco-card-editor";
const INTEGRATION_PLATFORM = "tplink_deco";
const DEFAULT_SECONDARY = "ip";
const DEFAULT_SORT = "name";
const DEFAULT_COLUMNS = 2;
const MAX_COLUMNS = 6;
const MIN_COLUMN_WIDTH = "240px";
const SECONDARY_OPTIONS = ["ip", "mac", "connection", "none"];
const SORT_OPTIONS = ["name", "download", "upload", "connection"];
const UNAVAILABLE_STATES = ["unavailable", "unknown"];

const CONNECTION_ICONS = {
  wired: "mdi:ethernet",
  band2_4: "mdi:wifi",
  band5: "mdi:wifi",
  band6: "mdi:wifi",
};

const TRANSLATIONS = {
  en: {
    "card.empty": "No TP-Link Deco clients found",
    "card.offline": "Offline",
    "card.download": "Download",
    "card.upload": "Upload",
    "conn.wired": "Wired",
    "conn.band2_4": "2.4 GHz",
    "conn.band5": "5 GHz",
    "conn.band6": "6 GHz",
    "editor.devices": "Clients to show (leave empty for all)",
    "editor.secondary_info": "Secondary info",
    "editor.secondary_info_ip": "IP address",
    "editor.secondary_info_mac": "MAC address",
    "editor.secondary_info_connection": "Connection type",
    "editor.secondary_info_none": "None",
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
    "card.download": "Download",
    "card.upload": "Upload",
    "conn.wired": "Cabo",
    "conn.band2_4": "2,4 GHz",
    "conn.band5": "5 GHz",
    "conn.band6": "6 GHz",
    "editor.devices": "Clientes a exibir (vazio = todos)",
    "editor.secondary_info": "Informação secundária",
    "editor.secondary_info_ip": "Endereço IP",
    "editor.secondary_info_mac": "Endereço MAC",
    "editor.secondary_info_connection": "Tipo de conexão",
    "editor.secondary_info_none": "Nenhuma",
    "editor.sort": "Ordenar por",
    "editor.sort_name": "Nome",
    "editor.sort_download": "Velocidade de download",
    "editor.sort_upload": "Velocidade de upload",
    "editor.sort_connection": "Tipo de conexão",
    "editor.columns": "Máximo de colunas",
    "editor.show_offline": "Mostrar clientes offline",
  },
};

const resolveLanguage = (hass) => {
  const language =
    (hass && (hass.locale?.language || hass.language || hass.selectedLanguage)) || "en";
  if (TRANSLATIONS[language]) return language;
  if (language.split("-")[0] === "pt") return "pt-BR";
  return "en";
};

const localize = (hass, key) =>
  TRANSLATIONS[resolveLanguage(hass)]?.[key] ?? TRANSLATIONS.en[key] ?? key;

const escapeHtml = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character],
  );

const connectionLabel = (hass, connectionType) => {
  const key = `conn.${connectionType}`;
  const label = localize(hass, key);
  return label === key ? (connectionType ?? "") : label;
};

const availableValue = (state) =>
  state && !UNAVAILABLE_STATES.includes(state.state) ? state.state : null;

const formatThroughput = (hass, state) =>
  availableValue(state) === null ? null : hass.formatEntityState(state);

class TpLinkDecoCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._signature = null;
  }

  static getConfigElement() {
    return document.createElement(EDITOR_TYPE);
  }

  static getStubConfig() {
    return {
      secondary_info: DEFAULT_SECONDARY,
      sort: DEFAULT_SORT,
      columns: DEFAULT_COLUMNS,
      show_offline: true,
    };
  }

  setConfig(config) {
    const secondary = config.secondary_info ?? DEFAULT_SECONDARY;
    if (!SECONDARY_OPTIONS.includes(secondary)) {
      throw new Error(`${CARD_TYPE}: "secondary_info" must be one of ${SECONDARY_OPTIONS.join(", ")}`);
    }
    const sort = config.sort ?? DEFAULT_SORT;
    if (!SORT_OPTIONS.includes(sort)) {
      throw new Error(`${CARD_TYPE}: "sort" must be one of ${SORT_OPTIONS.join(", ")}`);
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

  _clients() {
    const hass = this._hass;
    const entities = hass.entities || {};
    const devices = hass.devices || {};

    const entriesByDevice = {};
    for (const entry of Object.values(entities)) {
      if (entry.platform !== INTEGRATION_PLATFORM || !entry.device_id) continue;
      (entriesByDevice[entry.device_id] ??= []).push(entry);
    }

    const wantedDevices = this._config.devices ? new Set(this._config.devices) : null;
    const clients = [];

    for (const [deviceId, entries] of Object.entries(entriesByDevice)) {
      if (wantedDevices && !wantedDevices.has(deviceId)) continue;

      const tracker = entries.find((entry) => entry.entity_id.startsWith("device_tracker."));
      if (!tracker) continue;

      const entityIdByKey = {};
      for (const entry of entries) {
        if (entry.translation_key) entityIdByKey[entry.translation_key] = entry.entity_id;
      }
      const stateOf = (key) => (entityIdByKey[key] ? hass.states[entityIdByKey[key]] : null);

      const device = devices[deviceId] || {};
      const trackerState = hass.states[tracker.entity_id];
      const downloadState = stateOf("download");
      const uploadState = stateOf("upload");

      clients.push({
        deviceId,
        moreInfoEntity: entityIdByKey.ip || tracker.entity_id,
        name:
          device.name_by_user ||
          device.name ||
          trackerState?.attributes?.friendly_name ||
          tracker.entity_id,
        online: trackerState?.state === "home" || stateOf("connected")?.state === "on",
        connectionType: stateOf("connection_type")?.state,
        ip: availableValue(stateOf("ip")),
        mac: availableValue(stateOf("mac")),
        download: formatThroughput(hass, downloadState),
        upload: formatThroughput(hass, uploadState),
        downloadValue: Number(downloadState?.state) || 0,
        uploadValue: Number(uploadState?.state) || 0,
      });
    }

    const shown = this._config.showOffline ? clients : clients.filter((client) => client.online);
    const collator = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });
    shown.sort((left, right) => {
      if (left.online !== right.online) return left.online ? -1 : 1;
      switch (this._config.sort) {
        case "download":
          return right.downloadValue - left.downloadValue;
        case "upload":
          return right.uploadValue - left.uploadValue;
        case "connection":
          return collator.compare(left.connectionType || "", right.connectionType || "");
        default:
          return collator.compare(left.name, right.name);
      }
    });
    return shown;
  }

  _secondaryText(client) {
    const hass = this._hass;
    switch (this._config.secondaryInfo) {
      case "ip":
        return client.ip || "—";
      case "mac":
        return client.mac || "—";
      case "connection":
        return client.online
          ? connectionLabel(hass, client.connectionType)
          : localize(hass, "card.offline");
      default:
        return "";
    }
  }

  _render() {
    if (!this._hass) return;
    const hass = this._hass;
    const clients = this._clients();

    const signature = JSON.stringify([
      resolveLanguage(hass),
      this._config,
      clients.map((client) => [
        client.deviceId,
        client.name,
        client.online,
        client.connectionType,
        client.ip,
        client.mac,
        client.download,
        client.upload,
      ]),
    ]);
    if (signature === this._signature) return;
    this._signature = signature;

    const empty = `
      <ha-card class="empty">
        <ha-icon icon="mdi:router-wireless-off"></ha-icon>
        <span>${escapeHtml(localize(hass, "card.empty"))}</span>
      </ha-card>`;

    this.shadowRoot.innerHTML = `
      <style>${TpLinkDecoCard.styles}</style>
      <div class="grid" style="--columns:${this._config.columns}">
        ${clients.length ? clients.map((client) => this._renderClient(client)).join("") : empty}
      </div>`;

    this.shadowRoot.querySelectorAll(".client").forEach((element) => {
      element.addEventListener("click", () => this._showMoreInfo(element.dataset.entity));
      element.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        this._showMoreInfo(element.dataset.entity);
      });
    });
  }

  _renderClient(client) {
    const hass = this._hass;
    const icon = client.online
      ? CONNECTION_ICONS[client.connectionType] || "mdi:lan-connect"
      : "mdi:wifi-off";
    const secondary = this._secondaryText(client);
    const trailing = client.online
      ? `<div class="throughput">
          <span title="${escapeHtml(localize(hass, "card.download"))}">
            <ha-icon icon="mdi:arrow-down"></ha-icon>${escapeHtml(client.download || "—")}
          </span>
          <span title="${escapeHtml(localize(hass, "card.upload"))}">
            <ha-icon icon="mdi:arrow-up"></ha-icon>${escapeHtml(client.upload || "—")}
          </span>
        </div>`
      : `<span class="offline">${escapeHtml(localize(hass, "card.offline"))}</span>`;

    return `
      <ha-card
        class="client ${client.online ? "online" : "is-offline"}"
        data-entity="${escapeHtml(client.moreInfoEntity)}"
        role="button"
        tabindex="0"
        aria-label="${escapeHtml(client.name)}"
      >
        <ha-ripple></ha-ripple>
        <div class="content">
          <ha-tile-icon icon="${escapeHtml(icon)}"></ha-tile-icon>
          <ha-tile-info
            primary="${escapeHtml(client.name)}"
            ${secondary ? `secondary="${escapeHtml(secondary)}"` : ""}
          ></ha-tile-info>
          ${trailing}
        </div>
      </ha-card>`;
  }

  _showMoreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }),
    );
  }

  static get styles() {
    return `
      :host { display: block; }
      .grid {
        --columns: 1;
        --gap: var(--ha-space-2, 8px);
        display: grid;
        gap: var(--gap);
        grid-template-columns: repeat(
          auto-fill,
          minmax(max(${MIN_COLUMN_WIDTH}, calc((100% - (var(--columns) - 1) * var(--gap)) / var(--columns))), 1fr)
        );
      }
      .client {
        --tile-color: var(--state-device_tracker-home-color, var(--state-active-color));
        --ha-ripple-color: var(--tile-color);
        --ha-ripple-hover-opacity: 0.04;
        --ha-ripple-pressed-opacity: 0.12;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        outline: none;
      }
      .client:focus-visible { box-shadow: 0 0 0 2px var(--tile-color); }
      .client.is-offline { --tile-color: var(--state-inactive-color, var(--disabled-color)); }
      .content {
        position: relative;
        display: flex;
        align-items: center;
        gap: var(--ha-space-3, 12px);
        min-height: 56px;
        padding: 0 var(--ha-space-3, 12px);
        box-sizing: border-box;
      }
      ha-tile-icon { --tile-icon-color: var(--tile-color); }
      ha-tile-info { flex: 1 1 auto; min-width: 0; }
      .throughput {
        flex: none;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-s, 12px);
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
      }
      .throughput span { display: inline-flex; align-items: center; gap: 2px; }
      .throughput ha-icon { --mdc-icon-size: 14px; }
      .offline {
        flex: none;
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-s, 12px);
      }
      .empty {
        grid-column: 1 / -1;
        display: flex;
        align-items: center;
        gap: var(--ha-space-2, 8px);
        padding: var(--ha-space-4, 16px);
        color: var(--secondary-text-color);
      }
    `;
  }
}

class TpLinkDecoCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _schema() {
    const label = (key) => localize(this._hass, key);
    const select = (name, values) => ({
      name,
      selector: {
        select: {
          mode: "dropdown",
          options: values.map((value) => ({ value, label: label(`editor.${name}_${value}`) })),
        },
      },
    });
    return [
      {
        name: "devices",
        selector: { device: { multiple: true, filter: { integration: INTEGRATION_PLATFORM } } },
      },
      select("secondary_info", SECONDARY_OPTIONS),
      select("sort", SORT_OPTIONS),
      { name: "columns", selector: { number: { min: 1, max: MAX_COLUMNS, mode: "box" } } },
      { name: "show_offline", selector: { boolean: {} } },
    ];
  }

  _render() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (field) => localize(this._hass, `editor.${field.name}`);
      this._form.addEventListener("value-changed", (event) => {
        const config = { ...this._config, ...event.detail.value };
        for (const [key, value] of Object.entries(config)) {
          if (value === "" || value == null || (Array.isArray(value) && value.length === 0)) {
            delete config[key];
          }
        }
        config.type = this._config.type ?? `custom:${CARD_TYPE}`;
        this.dispatchEvent(
          new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }),
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

// The module is evaluated once per URL, and the URL carries the integration
// version: upgrading without a restart loads it a second time.
if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, TpLinkDecoCard);
  customElements.define(EDITOR_TYPE, TpLinkDecoCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: CARD_TYPE,
    name: "TP-Link Deco Card",
    description: "Lists the clients connected to the TP-Link Deco mesh with their address and throughput.",
    preview: true,
    documentationURL: "https://github.com/roquerodrigo/ha-tplink-deco",
  });

  console.info("%c tplink-deco-card ", "background:#4ABC96;color:#fff;border-radius:3px", "loaded");
}
