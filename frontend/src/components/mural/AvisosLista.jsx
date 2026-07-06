import AvisoItem from './AvisoItem'

export default function AvisosLista({ avisos, isAdmin, onDelete, onEdit }) {
  return avisos.map(aviso => (
    <AvisoItem
      key={aviso.id}
      aviso={aviso}
      isAdmin={isAdmin}
      onEdit={onEdit}
      onDelete={onDelete}
    />
  ))
}
