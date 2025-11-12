import { useRef, useCallback, useState } from 'react';

// Хук для открытия диалога выбора файлов (в проекте есть reactuse, но он еще test coverage, поэтому написал свой)
export function useFileDialog(options = {}) {
    const {
        accept = '*/*',
        maxFiles = 1,
        multiple = maxFiles > 1
    } = options;

    const inputRef = useRef(null);
    const [files, setFiles] = useState([]);
    const [error, setError] = useState(null);

    const reset = useCallback(() => {
        setFiles([]);
        setError(null);
        if (inputRef.current) {
            inputRef.current.value = '';
        }
    }, []);

    const open = useCallback(() => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = accept;
        input.multiple = multiple;
        input.style.display = 'none';

        input.addEventListener('change', (event) => {
            const selectedFiles = event.target.files;

            if (selectedFiles && selectedFiles.length > 0) {
                if (selectedFiles.length > maxFiles) {
                    setError(`Максимальное количество файлов: ${maxFiles}`);
                    setFiles([]);
                } else {
                    const filesArray = Array.from(selectedFiles);
                    setFiles(filesArray);
                    setError(null);
                }
            } else {
                setFiles([]);
            }

            inputRef.current = null;
            document.body.removeChild(input);
        });

        document.body.appendChild(input);
        inputRef.current = input;
        input.click();
    }, [accept, multiple, maxFiles]);

    return {
        open,
        files,
        reset,
        error
    };
}