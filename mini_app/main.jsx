import { createRoot } from 'react-dom/client';
import { MaxUI } from '@maxhub/max-ui';
import '@maxhub/max-ui/dist/styles.css';
import {App} from './App.jsx';
import './assets/styles/body.css';

const Root = () => (
    <MaxUI>
        <App />
    </MaxUI>
)

createRoot(document.getElementById('app')).render(<Root />);
