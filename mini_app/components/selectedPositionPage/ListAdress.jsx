import {CellList, CellSimple} from "@maxhub/max-ui";

export function ListAdress(props) {
    const handleItemClick = (item) => {
        if (props.onSelect) {
            props.onSelect(item);
        }
    };

    return (
        <CellList>
            {props.list.map((item, index) => {
                if (item.address_details.locality) {
                    return (
                        <div
                            key={index}
                            onClick={() => handleItemClick(item)}
                            style={{
                                cursor: 'pointer',
                                transition: 'background-color 0.2s'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = "light-dark(#f5f5f5, #2f3137)";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                            }}
                        >
                            <CellSimple
                                title={item.address_details.locality + ', ' + item.address_details.region}
                                subtitle={item.address_details.subregion}
                            />
                        </div>
                    );
                }
                return null;
            })}
        </CellList>
    );
}