export default function LogsActions({ fileRef, importing, logs, onExport, onImport }) {
  return (
    <div className="button-row">
      <label className="btn btn-outline clickable-label">
        {importing ? 'Importando...' : 'Importar Excel'}
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx,.xls"
          className="hidden-input"
          onChange={onImport}
          disabled={importing}
        />
      </label>
      <button className="btn btn-primary" onClick={onExport} disabled={!logs.length}>
        Exportar Excel
      </button>
    </div>
  )
}
