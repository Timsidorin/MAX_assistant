import {SearchInput} from "@maxhub/max-ui";
import {searchAdress} from "@api/gps.js";
import { useDebounceValue } from '@siberiacancode/reactuse';
import {useState, useEffect, useRef} from "react";
import {ListAdress} from "@components/selectedPositionPage/ListAdress.jsx";

export function InputAdressSearch(props) {
    const [value, setValue] = useState('');
    const debouncedValue = useDebounceValue(value, 500);
    const [listAdress, setListAdress] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef(null);

    useEffect(() => {
        const fetchAddress = async () => {
            if (debouncedValue.length > 3) {
                try {
                    const response = await searchAdress({q: debouncedValue});
                    setListAdress(response.data.results);
                    setIsOpen(true);
                    console.log(response);
                } catch (error) {
                    console.error('Error fetching address:', error);
                    setListAdress([]);
                    setIsOpen(false);
                }
            } else {
                setListAdress([]);
                setIsOpen(false);
            }
        };

        fetchAddress();
    }, [debouncedValue]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleSelectAddress = (address) => {
        if (props.onSelect) {
            props.onSelect(address);
        }
        setValue(address.name);
        setIsOpen(false);
    };

    return (
        <div ref={wrapperRef} style={{ position: 'relative', width: '100%', marginBottom: '10px'}}>
            <SearchInput
                value={value}
                mode="secondary"
                placeholder="Поиск"
                onChange={(e) => {
                    setValue(e.target.value);
                    if (e.target.value.length > 3) {
                        setIsOpen(true);
                    } else {
                        setIsOpen(false);
                    }
                }}
                onFocus={() => {
                    if (listAdress.length > 0) {
                        setIsOpen(true);
                    }
                }}
            />

            {isOpen && listAdress.length > 0 && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    backgroundColor: "light-dark(#edeef2, #17181c)",
                    border: '1px solid light-dark(#edeef2, #17181c)',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                    zIndex: 1000,
                    maxHeight: '300px',
                    overflowY: 'auto',
                    marginTop: '4px'
                }}>
                    <ListAdress
                        list={listAdress}
                        onSelect={handleSelectAddress}
                    />
                </div>
            )}
        </div>
    );
}