import { SideNavigation } from '@cloudscape-design/components';
const Sidenavigation = () => {
    return (<SideNavigation
        header={{
            href: '#',
            text: 'Service name',
        }}
        items={[{ type: 'link', text: `Page #1`, href: `#` }]}
    />)
}
export default Sidenavigation;