export default function LogsActions({ exporting, fileRef, importing, logs, onExport, onImport }) {
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
      <button className="btn btn-primary" onClick={onExport} disabled={exporting || !logs.length}>
        {exporting ? 'Exportando...' : 'Exportar Excel'}
      </button>
    </div>
  )
}
