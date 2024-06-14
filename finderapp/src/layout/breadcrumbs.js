import { BreadcrumbGroup } from '@cloudscape-design/components';
const Breadcrumbs = () => {
    return (<BreadcrumbGroup
        items={[
            { text: 'Home', href: '/' },
            { text: 'Pages', href: '#' },
        ]}
    />)
}

export default Breadcrumbs;