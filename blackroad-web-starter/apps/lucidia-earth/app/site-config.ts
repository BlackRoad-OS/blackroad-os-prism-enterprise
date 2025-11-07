import type { Route } from "next";

    type NavigationItem = {
      label: string;
      href: Route<string>;
    };

    type HeroAction = {
      label: string;
      href: Route<string>;
    };

    type HeroConfig = {
      eyebrow: string;
      title: string;
      description: string;
      primary: HeroAction;
      secondary: HeroAction;
    };

    export const navigation = [
  {
    "label": "Home",
    "href": "/"
  },
  {
    "label": "About",
    "href": "/about"
  },
  {
    "label": "Contact",
    "href": "/contact"
  },
  {
    "label": "Docs",
    "href": "/docs"
  },
  {
    "label": "Privacy",
    "href": "/privacy"
  },
  {
    "label": "Terms",
    "href": "/terms"
  },
  {
    "label": "Status",
    "href": "/status"
  }
] as const satisfies NavigationItem[];

    export const siteConfig = {
      name: "Lucidia Earth",
      domain: "lucidia.earth",
      navigation,
    };

    export const hero = {
      eyebrow: "Creator campus",
      title: "A city-in-the-garden for imaginative builders",
      description: "Residencies, guilds, and studios co-create regenerative futures across the Lucidia campus network.",
      primary: {"label": "Apply for residency", "href": "/contact"},
      secondary: {"label": "Tour the grounds", "href": "/about"}
    } as const satisfies HeroConfig;

    export const features = [
  {
    "title": "Immersive districts",
    "description": "Studios, labs, and sanctuaries designed for prototyping ideas with nature as collaborator."
  },
  {
    "title": "Guild ecosystem",
    "description": "Craft guilds pair mentors with residents to accelerate craft and community impact."
  },
  {
    "title": "Shared stewardship",
    "description": "Campus infrastructure is governed by residents with transparent decision rituals."
  }
];

    export const story = [
  {
    "title": "Seeds of Lucidia",
    "body": "We reclaimed industrial land and replanted it as a commons for creators."
  },
  {
    "title": "Living classrooms",
    "body": "Programs merge ecology, craft, and technology in sensory-rich studios."
  },
  {
    "title": "Expanding the canopy",
    "body": "We are developing satellite gardens and virtual residencies to widen access."
  }
];

    export const contactConfig = {
      intro: "Our community team curates residencies, partnerships, and events. Share your practice to begin.",
      email: "community@lucidia.earth"
    };
