export const TypesDropdown = (props) => {

    const onChange = props.onChange;
    const currentDocType = props.currentDocType;
    const documentTypes = props.documentTypes;

    const handleChange = (event) => {
        onChange(event.target.value);
    }

    return (
        <div className="">
            <select
                className="form-select form-select-lg mb-3"
                name={"select"}
                value={currentDocType}
                onChange={handleChange}
            >
                {Object.keys(documentTypes).map(key => (
                    <option key={key} value={key}>{documentTypes[key].name}</option>
                ))}
            </select>
        </div>
    )
}