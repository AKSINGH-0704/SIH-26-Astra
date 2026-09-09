import { redirect } from "next/navigation";

/**
 * The Command Centre takes this route once the hazard engine and map surface
 * land. Until then the root goes to the screen that is genuinely built, rather
 * than to an empty dashboard.
 */
export default function Home() {
  redirect("/model");
}
